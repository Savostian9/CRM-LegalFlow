from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('crm_app', '0015_rename_crm_app_task_created_by_idx_crm_app_tas_created_a59b7a_idx_and_more'),
	]

	operations = [
		migrations.CreateModel(
			name='UserPermissionSet',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('can_create_client', models.BooleanField(default=True)),
				('can_edit_client', models.BooleanField(default=True)),
				('can_delete_client', models.BooleanField(default=True)),
				('can_create_case', models.BooleanField(default=True)),
				('can_edit_case', models.BooleanField(default=True)),
				('can_delete_case', models.BooleanField(default=True)),
				('can_create_task', models.BooleanField(default=True)),
				('can_edit_task', models.BooleanField(default=True)),
				('can_delete_task', models.BooleanField(default=True)),
				('can_upload_files', models.BooleanField(default=True)),
				('can_invite_users', models.BooleanField(default=True)),
				('can_manage_users', models.BooleanField(default=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='permset', to='crm_app.user')),
			],
		),
	]
