from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a direct test email to verify SMTP delivery. Usage: --to you@example.com'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, required=True, help='Recipient email address')

    def handle(self, *args, **options):
        to = options['to']
        if not to:
            raise CommandError('Provide --to email')
        subject = 'LegalFlow test email'
        message = 'This is a test email from LegalFlow via Django.'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        self.stdout.write(f'Sending test email to <{to}> from <{from_email}>')
        try:
            sent = send_mail(subject, message, from_email, [to], fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f'Test email sent, result={sent}'))
        except Exception as e:
            raise CommandError(f'Failed to send test email: {e}')
