"""
Management command: migrate_media_to_s3

Purpose
-------
Copy existing media files from the server's local MEDIA_ROOT into the current
DEFAULT_FILE_STORAGE (e.g., S3 via django-storages). This is a one-time
migration tool for when you switch from local storage to S3 and need your
previously uploaded files to appear under the new storage backend without
changing DB references.

Usage
-----
  python manage.py migrate_media_to_s3 --dry-run
  python manage.py migrate_media_to_s3

Options
-------
  --dry-run     : Print planned actions without uploading
  --overwrite   : Re-upload even if object/key already exists in target storage
  --prefix PFX  : Only process keys starting with PFX (e.g., client_documents/)
  --scan-media  : Walk entire MEDIA_ROOT (all files), not only DB-referenced
                  FileFields
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Tuple

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandParser
from django.db.models.fields.files import FileField


def iter_filefields_models() -> Iterable[Tuple[object, list[FileField]]]:
    """Yield pairs (ModelClass, [FileField, ...]) for all models that have FileFields."""
    for model in apps.get_models():
        try:
            fields = [f for f in model._meta.get_fields() if isinstance(f, FileField)]
        except Exception:
            fields = []
        if fields:
            yield model, fields


class Command(BaseCommand):
    help = (
        "Copy existing media files from local MEDIA_ROOT to the current default storage (e.g., S3)."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only print what would be copied",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Re-upload even if object already exists in target storage",
        )
        parser.add_argument(
            "--prefix",
            default="",
            help="Limit to file keys starting with this prefix (e.g., client_documents/)",
        )
        parser.add_argument(
            "--scan-media",
            action="store_true",
            help="Walk entire MEDIA_ROOT (all files), not just DB-referenced ones",
        )

    def handle(self, *args, **opts) -> None:
        dry: bool = bool(opts.get("dry_run"))
        overwrite: bool = bool(opts.get("overwrite"))
        prefix: str = str(opts.get("prefix") or "")
        scan_media: bool = bool(opts.get("scan_media"))

        media_root = Path(settings.MEDIA_ROOT or "media").resolve()
        if not media_root.exists():
            self.stderr.write(self.style.WARNING(f"MEDIA_ROOT does not exist: {media_root}"))

        # Quick info on storage backend
        storage_cls = default_storage.__class__.__module__ + "." + default_storage.__class__.__name__
        self.stdout.write(
            self.style.NOTICE(
                f"Target storage: {storage_cls}\nMEDIA_ROOT (source): {media_root}"
            )
        )

        processed: set[str] = set()
        copied = 0
        skipped = 0
        missing_local = 0

        def normalized_key(p: Path) -> str:
            return str(p).replace("\\", "/")

        def upload(name: str, local_path: Path) -> None:
            nonlocal copied, skipped, missing_local
            if not name:
                return
            if name in processed:
                return
            processed.add(name)

            if prefix and not name.startswith(prefix):
                return
            if not local_path.exists():
                missing_local += 1
                self.stdout.write(f"LOCAL MISSING: {name}")
                return
            if not overwrite and default_storage.exists(name):
                skipped += 1
                return

            if dry:
                self.stdout.write(f"COPY: {name}")
                return

            # Ensure parent directories (local backend) — S3 backends ignore this
            try:
                with local_path.open("rb") as fh:
                    default_storage.save(name, File(fh))
                copied += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"ERROR uploading {name}: {e}"))

        if scan_media:
            # Full walk of MEDIA_ROOT
            if media_root.exists():
                for path in media_root.rglob("*"):
                    if path.is_file():
                        rel = normalized_key(path.relative_to(media_root))
                        upload(rel, path)
        else:
            # Only DB-referenced FileFields
            for model, ffields in iter_filefields_models():
                try:
                    qs = model._default_manager.all().iterator()
                except Exception:
                    continue
                for obj in qs:
                    for f in ffields:
                        try:
                            ffile = getattr(obj, f.name, None)
                            name = getattr(ffile, "name", "") or ""
                        except Exception:
                            name = ""
                        if not name:
                            continue
                        local_path = media_root / name
                        upload(name, local_path)

        self.stdout.write(
            self.style.SUCCESS(
                f"DONE dry={dry} overwrite={overwrite} | copied={copied} skipped={skipped} missing_local={missing_local}"
            )
        )
