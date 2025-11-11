import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from crm_app.models import UploadedFile, User, Company

try:
    import boto3  # type: ignore
except ImportError:  # graceful degraded mode
    boto3 = None


class Command(BaseCommand):
    help = "Scan S3 bucket for orphaned blobs (files present in storage but missing DB records)."

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='', help='Limit scan to a specific prefix (e.g. client_documents/)')
        parser.add_argument('--limit', type=int, default=0, help='Maximum number of keys to list (0 = all)')
        parser.add_argument('--delete-orphans', action='store_true', help='Delete orphaned blobs after confirmation')
        parser.add_argument('--dry-run', action='store_true', help='Do not delete, just report (default)')

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_S3', False):
            self.stderr.write('S3 not enabled (USE_S3=0); aborting scan.')
            return
        if boto3 is None:
            self.stderr.write('boto3 not installed; cannot list bucket objects.')
            return

        bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
        endpoint = os.getenv('AWS_S3_ENDPOINT_URL')
        region = os.getenv('AWS_S3_REGION_NAME') or None
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        custom_domain = os.getenv('AWS_S3_CUSTOM_DOMAIN')

        if not all([bucket, endpoint, access_key, secret_key]):
            self.stderr.write('Missing S3 credentials/endpoint env variables.')
            return

        prefix = options['prefix']
        limit = options['limit']
        delete_flag = options['delete_orphans'] and not options['dry_run']

        s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        self.stdout.write(f"Scanning bucket={bucket} prefix='{prefix}' limit={limit or 'ALL'} delete_orphans={delete_flag}")

        # Build a set of all known file names from DB (for efficient lookup)
        db_file_names = set(UploadedFile.objects.values_list('file', flat=True))
        db_file_names.update(User.objects.exclude(avatar='').values_list('avatar', flat=True))
        db_file_names.update(Company.objects.exclude(logo='').values_list('logo', flat=True))

        paginator_next = None
        total_keys = 0
        orphan_keys = []

        while True:
            kwargs = {'Bucket': bucket, 'Prefix': prefix}
            if paginator_next is not None:
                kwargs['ContinuationToken'] = paginator_next
            resp = s3.list_objects_v2(**kwargs)
            contents = resp.get('Contents', [])
            for obj in contents:
                key = obj['Key']
                total_keys += 1
                if limit and total_keys > limit:
                    break
                if key not in db_file_names:
                    orphan_keys.append(key)
            if limit and total_keys >= limit:
                break
            if not resp.get('IsTruncated'):
                break
            paginator_next = resp.get('NextContinuationToken')

        self.stdout.write(f"Total listed keys: {total_keys}")
        self.stdout.write(f"Orphaned keys: {len(orphan_keys)}")

        for k in orphan_keys[:50]:  # show first 50
            self.stdout.write(f"  ORPHAN: {k}")
        if len(orphan_keys) > 50:
            self.stdout.write("  ... (truncated) ...")

        if delete_flag and orphan_keys:
            confirm = input(f"Delete {len(orphan_keys)} orphaned objects? Type 'yes' to confirm: ").strip().lower()
            if confirm == 'yes':
                deleted = 0
                for k in orphan_keys:
                    try:
                        s3.delete_object(Bucket=bucket, Key=k)
                        deleted += 1
                    except Exception as err:
                        self.stderr.write(f"Failed to delete {k}: {err}")
                self.stdout.write(f"Deleted {deleted} orphan objects.")
            else:
                self.stdout.write('Aborted deletion; no changes made.')
        else:
            if orphan_keys:
                self.stdout.write("Run again with --delete-orphans to remove them (will prompt).")
            else:
                self.stdout.write("No orphans detected.")