from django.core.management.base import BaseCommand
from django.utils import timezone
from crm_app.models import Notification, Reminder

class Command(BaseCommand):
    help = "Remove duplicate reminder notifications: deletes 'Создано напоминание:' entries and keeps single per (reminder, created_by)."

    def handle(self, *args, **options):
        # 1. Удаляем «создано напоминание»
        removed_created = Notification.objects.filter(title__startswith='Создано напоминание:').delete()[0]
        self.stdout.write(f"Removed creation notifications: {removed_created}")
        # 2. Удаляем уведомления где есть client.created_by и user != created_by
        mismatched = 0
        for n in Notification.objects.select_related('client', 'client__created_by').exclude(reminder__isnull=True):
            cb = getattr(getattr(n.client, 'created_by', None), 'id', None)
            if cb and n.user_id != cb:
                n.delete(); mismatched += 1
        self.stdout.write(f"Removed mismatched manager notifications: {mismatched}")
        # 3. Дедуп по (user,reminder)
        dups = 0
        for rem_id in Notification.objects.exclude(reminder__isnull=True).values_list('reminder_id', flat=True).distinct():
            seen = set()
            for n in Notification.objects.filter(reminder_id=rem_id).order_by('id'):
                key = (n.user_id, n.reminder_id)
                if key in seen:
                    n.delete(); dups += 1
                else:
                    seen.add(key)
        self.stdout.write(self.style.SUCCESS(f"Duplicate (user,reminder) removed: {dups}"))