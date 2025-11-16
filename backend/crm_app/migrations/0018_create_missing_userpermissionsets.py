from django.db import migrations


def create_missing_permissionsets(apps, schema_editor):
    """Create UserPermissionSet for all users who don't have one."""
    User = apps.get_model('crm_app', 'User')
    UserPermissionSet = apps.get_model('crm_app', 'UserPermissionSet')
    
    # Get all users who don't have a UserPermissionSet
    users_without_permset = []
    for user in User.objects.all():
        try:
            user.permset
        except UserPermissionSet.DoesNotExist:
            users_without_permset.append(user)
    
    # Create UserPermissionSet for each user with default permissions (all True)
    permission_sets = []
    for user in users_without_permset:
        permission_sets.append(
            UserPermissionSet(
                user=user,
                can_create_client=True,
                can_edit_client=True,
                can_delete_client=True,
                can_create_case=True,
                can_edit_case=True,
                can_delete_case=True,
                can_create_task=True,
                can_edit_task=True,
                can_delete_task=True,
                can_upload_files=True,
                can_invite_users=True,
                can_manage_users=True,
            )
        )
    
    # Bulk create all permission sets
    if permission_sets:
        UserPermissionSet.objects.bulk_create(permission_sets)


class Migration(migrations.Migration):
    dependencies = [
        ('crm_app', '0017_userpermissionset_recover'),
    ]

    operations = [
        migrations.RunPython(create_missing_permissionsets, migrations.RunPython.noop),
    ]
