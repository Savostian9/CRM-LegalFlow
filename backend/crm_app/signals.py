from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, time as dtime

from .models import Reminder, Notification, User

INTERNAL_NOTIFY_ROLES = ['ADMIN', 'LEAD', 'LAWYER', 'MANAGER', 'ASSISTANT']


@receiver(post_save, sender=Reminder)
def reminder_created_notification(sender, instance: Reminder, created: bool, **kwargs):
    """Create a notification for internal staff when a new Reminder is created.

    Avoid duplicates: if a notification already exists for (user, reminder) we skip.
    Does not mark as read. Title kept short; message contains date/time if present.
    """
    # ОТКЛЮЧЕНО: намеренно ничего не делаем чтобы не создавать дубли.
    return
