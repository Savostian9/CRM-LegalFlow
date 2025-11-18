from django.db import migrations

def add_column_if_not_exists(apps, schema_editor):
    table_name = 'crm_app_document'
    column_name = 'name'
    
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN IF NOT EXISTS "{column_name}" varchar(255) NULL;')
    elif schema_editor.connection.vendor == 'sqlite':
        cursor = schema_editor.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        if column_name not in columns:
            schema_editor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" varchar(255) NULL;')

class Migration(migrations.Migration):

    dependencies = [
        ('crm_app', '0021_alter_document_name'),
    ]

    operations = [
        migrations.RunPython(add_column_if_not_exists),
    ]
