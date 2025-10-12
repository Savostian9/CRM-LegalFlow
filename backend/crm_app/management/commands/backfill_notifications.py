from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_app.models import Reminder, Notification, User


class Command(BaseCommand):
    help = "Create missing Notification rows for already sent reminders (sent_at IS NOT NULL) for all internal roles in the client's company. Safe (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only report what would be created')
        parser.add_argument('--limit', type=int, default=5000, help='Limit reminders processed (default 5000)')

    def handle(self, *args, **options):
        dry = options['dry_run']
        limit = options['limit']
        qs = Reminder.objects.select_related('client', 'client__created_by', 'client__user').filter(sent_at__isnull=False).order_by('-sent_at')[:limit]
        self.stdout.write(f"Scanning sent reminders: {qs.count()}")
        created = 0
        now = timezone.now()
        # Только для ответственного менеджера (client.created_by)
        for rem in qs:
            client = rem.client
            if not client:
                continue
            # Если есть ответственный менеджер — уведомляем его.
            # Если нет — создаём одно уведомление для fallback-пользователя компании.
            if getattr(client, 'created_by', None):
                staff = [client.created_by]
            else:
                fallback_user = None
                try:
                    company = getattr(getattr(client, 'user', None), 'company', None)
                    if company:
                        fallback_user = getattr(company, 'owner', None)
                        if not fallback_user:
                            fallback_user = company.users.filter(role__in=['ADMIN', 'LEAD']).order_by('id').first()
                        if not fallback_user:
                            fallback_user = company.users.filter(is_client=False).order_by('id').first()
                except Exception:
                    fallback_user = None
                if not fallback_user:
                    # Нет куда отправить — пропускаем.
                    continue
                staff = [fallback_user]
            doc_name = rem.get_reminder_type_display()
            title = f"Напоминание: {doc_name} (ранее отправлено)"
            msg_preview = f"Клиент: {client.first_name} {client.last_name} ({client.email})" if client else ''
            scheduled_dt = rem.sent_at or now
            for u in staff:
                if Notification.objects.filter(user=u, reminder=rem).exists():
                    continue
                created += 1
                if not dry:
                    Notification.objects.create(
                        user=u,
                        client=client,
                        reminder=rem,
                        title=title[:200],
                        message=msg_preview,
                        source='REMINDER',
                        visible_at=now,
                        scheduled_for=scheduled_dt,
                    )
        self.stdout.write(self.style.SUCCESS(f"Missing notifications created: {created}{' (dry-run)' if dry else ''}"))
