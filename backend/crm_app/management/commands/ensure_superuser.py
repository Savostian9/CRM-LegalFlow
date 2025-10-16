from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create or update a superuser with given email and password. Usage: manage.py ensure_superuser --email <email> --password <password>"

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email for the superuser')
        parser.add_argument('--password', required=True, help='Password for the superuser')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email'].strip().lower()
        password = options['password']
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email,
        })
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(('Created' if created else 'Updated') + f" superuser: {email}"))
