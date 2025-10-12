from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from crm_app.models import Client, Reminder
from datetime import timedelta


class Command(BaseCommand):
    help = 'Create a test reminder using reminder_date/reminder_time. Use --client-id or --email; optional --minutes-offset to shift time.'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=int, help='ID of the client')
        parser.add_argument('--email', type=str, help='Client email to match (exact)')
        parser.add_argument('--minutes-offset', type=int, default=0, help='Shift minutes relative to now (negative for past)')

    def handle(self, *args, **options):
        c = None
        cid = options.get('client_id')
        email = options.get('email')
        if cid:
            c = Client.objects.filter(id=cid).first()
            if not c:
                raise CommandError(f'Client with id={cid} not found')
        elif email:
            c = Client.objects.filter(email=email).first()
            if not c:
                raise CommandError(f'Client with email={email} not found')
        else:
            c = Client.objects.order_by('id').first()
            if not c:
                self.stdout.write('No clients found')
                return
        now = timezone.localtime() + timedelta(minutes=options.get('minutes_offset') or 0)
        r, _ = Reminder.objects.get_or_create(client=c, reminder_type='UMOWA_PRACA_ZLECENIA')
        r.reminder_date = now.date()
        r.reminder_time = now.time().replace(second=0, microsecond=0)
        r.sent_at = None
        r.note = 'TEST (date+time)'
        r.save()
        self.stdout.write(f'Created/updated reminder {r.id} for client {c.id} at {r.reminder_date} {r.reminder_time}')
