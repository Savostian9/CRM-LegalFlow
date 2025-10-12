from django.core.management.base import BaseCommand
from crm_app.models import User


class Command(BaseCommand):
    help = "Create or update a development user with known credentials"

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@example.com')
        parser.add_argument('--username', default='admin')
        parser.add_argument('--password', default='Admin123!')

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']

        user, created = User.objects.get_or_create(email=email, defaults={
            'username': username,
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
        })
        # Ensure fields and password are set as expected
        user.username = username
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created dev user {email} / {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"Updated dev user {email} / {username}"))
        self.stdout.write(self.style.SUCCESS("Password set and user active."))
