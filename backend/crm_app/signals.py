from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, time as dtime

from .models import Reminder, Notification, User, Company, UploadedFile
from django.core.files.storage import default_storage

INTERNAL_NOTIFY_ROLES = ['ADMIN', 'LEAD', 'LAWYER', 'MANAGER', 'ASSISTANT']


@receiver(post_save, sender=Reminder)
def reminder_created_notification(sender, instance: Reminder, created: bool, **kwargs):
    """Create a notification for internal staff when a new Reminder is created.

    Avoid duplicates: if a notification already exists for (user, reminder) we skip.
    Does not mark as read. Title kept short; message contains date/time if present.
    """
    # ОТКЛЮЧЕНО: намеренно ничего не делаем чтобы не создавать дубли.
    return


def _safe_delete_filefield(file_field):
    try:
        if file_field and getattr(file_field, 'name', None):
            name = file_field.name
            # Use the field's own storage if available, fall back to default
            storage = getattr(file_field, 'storage', default_storage)
            try:
                if storage.exists(name):
                    storage.delete(name)
            except Exception:
                # Even if exists() is not supported, attempt delete and ignore errors
                try:
                    storage.delete(name)
                except Exception:
                    pass
    except Exception:
        # Never break deletion transaction due to storage errors
        pass


@receiver(post_delete, sender=UploadedFile)
def delete_uploadedfile_blob(sender, instance: UploadedFile, **kwargs):
    """When UploadedFile DB record is removed, delete the underlying blob in storage."""
    _safe_delete_filefield(getattr(instance, 'file', None))


@receiver(post_delete, sender=User)
def delete_user_avatar_blob(sender, instance: User, **kwargs):
    _safe_delete_filefield(getattr(instance, 'avatar', None))


@receiver(post_delete, sender=Company)
def delete_company_logo_blob(sender, instance: Company, **kwargs):
    _safe_delete_filefield(getattr(instance, 'logo', None))
