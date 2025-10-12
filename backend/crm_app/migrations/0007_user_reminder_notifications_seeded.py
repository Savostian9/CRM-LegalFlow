from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm_app', '0006_alter_invite_role_alter_user_role_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reminder_notifications_seeded',
            field=models.BooleanField(default=False),
        ),
    ]
