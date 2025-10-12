from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('crm_app', '0007_user_reminder_notifications_seeded'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='visible_at',
            field=models.DateTimeField(null=True, blank=True, help_text='Если задано — показывать начиная с этого времени'),
        ),
        migrations.AddField(
            model_name='notification',
            name='scheduled_for',
            field=models.DateTimeField(null=True, blank=True, help_text='Запланированное время события (из напоминания)'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['visible_at'], name='crm_app_not_visible__idx'),
        ),
    ]
