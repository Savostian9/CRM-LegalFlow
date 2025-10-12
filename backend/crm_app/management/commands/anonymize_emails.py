from django.core.management.base import BaseCommand
from crm_app.models import User, Client


class Command(BaseCommand):
    help = "Anonymize (clean) all emails in User and Client tables by replacing with placeholders."

    def handle(self, *args, **options):
        # Anonymize User emails
        users = User.objects.all().order_by('id')
        for i, user in enumerate(users, start=1):
            new_email = f"user{i}@example.com"
            if user.email != new_email:
                user.email = new_email
                # Ensure username remains consistent if used for auth backend
                if not user.username:
                    user.username = f"user{i}"
                user.save(update_fields=["email", "username"])   # keep unique constraints intact

        # Anonymize Client emails to match their related user email
        clients = Client.objects.select_related('user').all().order_by('id')
        for client in clients:
            if client.user and client.email != client.user.email:
                client.email = client.user.email
                client.save(update_fields=["email"])

        self.stdout.write(self.style.SUCCESS("Emails anonymized successfully."))
