from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Activate legacy users who have usable passwords (to fix login after model changes)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only show what would change')

    def handle(self, *args, **options):
        User = get_user_model()
        dry = options.get('dry_run')
        total = 0
        activated = 0
        skipped_unusable = 0
        qs = User.objects.all()
        for u in qs:
            total += 1
            if not u.is_active:
                if u.has_usable_password():
                    if dry:
                        self.stdout.write(f"Would activate: {u.email} (id={u.id})")
                    else:
                        u.is_active = True
                        u.save(update_fields=['is_active'])
                        self.stdout.write(f"Activated: {u.email} (id={u.id})")
                    activated += 1
                else:
                    skipped_unusable += 1
        self.stdout.write(self.style.SUCCESS(
            f"Done. Users scanned={total}, activated={activated}, skipped_no_password={skipped_unusable}"
        ))
