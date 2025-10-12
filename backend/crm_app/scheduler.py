import threading
import time
import logging
from typing import Optional

from django.conf import settings
from django.core.management import call_command


logger = logging.getLogger(__name__)

_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()
_started = False


def _loop():
    interval = int(getattr(settings, 'REMINDER_SCHEDULER_INTERVAL_SECONDS', 60))
    logger.info("Reminder scheduler started with interval=%ss", interval)
    while not _stop_event.is_set():
        try:
            call_command('send_reminders')
        except Exception as e:
            logger.exception("Reminder scheduler cycle failed: %s", e)
        # Sleep with event to allow graceful stop
        _stop_event.wait(interval)
    logger.info("Reminder scheduler stopped")


def start_scheduler():
    global _thread, _started
    if _started and _thread and _thread.is_alive():
        return
    _stop_event.clear()
    _thread = threading.Thread(target=_loop, name="reminder-scheduler", daemon=True)
    _thread.start()
    _started = True


def stop_scheduler(timeout: float | None = None):
    _stop_event.set()
    if _thread and _thread.is_alive():
        _thread.join(timeout=timeout)
