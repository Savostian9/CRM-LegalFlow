from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_app', '0008_notification_schedule_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='notes',
            field=models.TextField(blank=True, default='', verbose_name='Заметки'),
        ),
    ]