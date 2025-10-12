from django.db import migrations


def add_created_at_column(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("PRAGMA table_info(crm_app_client)")
        cols = [row[1] for row in cursor.fetchall()]
        if 'created_at' in cols:
            return
        # Add column (SQLite syntax). No NOT NULL to avoid issues; we'll backfill values.
        cursor.execute("ALTER TABLE crm_app_client ADD COLUMN created_at DATETIME")
        # Backfill with current timestamp for existing rows
        cursor.execute("UPDATE crm_app_client SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")


def noop_reverse(apps, schema_editor):
    # Don't drop the column on reverse
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('crm_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_created_at_column, noop_reverse),
    ]
