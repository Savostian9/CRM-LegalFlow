from django.db import migrations, models
import django.conf

class Migration(migrations.Migration):
    dependencies = [
        ('crm_app', '0013_alter_task_task_type'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='created_by',
            field=models.ForeignKey(null=True, blank=True, on_delete=models.SET_NULL, related_name='created_tasks', to=django.conf.settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['created_by'], name='crm_app_task_created_by_idx'),
        ),
    ]
