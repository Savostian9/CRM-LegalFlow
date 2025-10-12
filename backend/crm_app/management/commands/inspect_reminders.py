from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from crm_app.models import Client, Reminder


class Command(BaseCommand):
    help = 'Inspect a client email and reminders. Use --client-id or --email.'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=int, help='ID of the client')
        parser.add_argument('--email', type=str, help='Client email to match (exact)')

    def handle(self, *args, **options):
        cid = options.get('client_id')
        email = options.get('email')
        client = None
        if cid:
            client = Client.objects.filter(id=cid).first()
        elif email:
            client = Client.objects.filter(email=email).first()
        if not client:
            raise CommandError('Client not found')

        self.stdout.write(f'Client #{client.id}: {client.first_name} {client.last_name}')
        self.stdout.write(f'Email: {client.email}')
        now = timezone.localtime()
        self.stdout.write(f'Now: {now} (tz-aware)')
        reminders = client.reminders.all().order_by('reminder_type')
        if not reminders:
            self.stdout.write('No reminders')
            return
        for r in reminders:
            self.stdout.write(f'- Reminder #{r.id} type={r.reminder_type} date={r.reminder_date} time={r.reminder_time} sent_at={r.sent_at}')
