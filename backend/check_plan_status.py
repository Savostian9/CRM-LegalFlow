import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crm_app.models import User

email = 'mirabsurda@outlook.com'
user = User.objects.filter(email=email).first()

if user and user.company:
    print(f"Company: {user.company.name}")
    print(f"Plan: {user.company.plan}")
    print(f"Status: {user.company.subscription_status}")
else:
    print("User or company not found")
