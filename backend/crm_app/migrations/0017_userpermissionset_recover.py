from django.db import migrations


def ensure_userpermissionset_table(apps, schema_editor):
    Model = apps.get_model('crm_app', 'UserPermissionSet')
    # Try to create the table if it does not actually exist (previous empty migration applied earlier)
    existing_tables = schema_editor.connection.introspection.table_names()
    if Model._meta.db_table in existing_tables:
        return
    # Use Django's schema_editor to create everything (fields, constraints, indexes)
    schema_editor.create_model(Model)


class Migration(migrations.Migration):
    dependencies = [
        ('crm_app', '0016_user_permission_flags'),
    ]

    operations = [
        migrations.RunPython(ensure_userpermissionset_table, migrations.RunPython.noop),
    ]
