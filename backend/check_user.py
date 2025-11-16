import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from crm_app.models import User, UserPermissionSet

email = 'headbutthecrossbar@gmail.com'
user = User.objects.filter(email=email).first()

if user:
    print(f"User found: ID={user.id}, email={user.email}, role={user.role}")
    try:
        permset = user.permset
        print(f"Has UserPermissionSet: YES (ID={permset.id})")
        print(f"  can_create_client={permset.can_create_client}")
        print(f"  can_edit_client={permset.can_edit_client}")
    except UserPermissionSet.DoesNotExist:
        print("Has UserPermissionSet: NO - THIS IS THE PROBLEM!")
else:
    print(f"User with email {email} NOT FOUND")
