from django.apps import AppConfig
import os
import sys


def _should_start_scheduler() -> bool:
    """
    Decide whether to start the in-process reminder scheduler.

    - Avoid starting during management commands like migrate, collectstatic, tests, etc.
    - Start for runserver (only in the reloader child process where RUN_MAIN=true).
    - For other contexts (e.g., WSGI), start once per process.
    """
    from django.conf import settings

    if not getattr(settings, 'ENABLE_REMINDER_SCHEDULER', True):
        return False

    # Common management commands where we DON'T want background threads
    block_cmds = {
        'migrate', 'makemigrations', 'collectstatic', 'shell', 'createsuperuser',
        'dbshell', 'loaddata', 'dumpdata', 'inspectdb', 'test', 'check', 'send_reminders'
    }
    if len(sys.argv) > 1 and sys.argv[1] in block_cmds:
        return False

    # When running the dev server with autoreload, ready() is invoked twice; only start in main process
    run_main = os.environ.get('RUN_MAIN')
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        return run_main == 'true'

    # For other entrypoints (e.g., WSGI servers), best-effort start once per process
    return True


class CrmAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm_app'

    def ready(self):
        # Lazy import to avoid side-effects during app registry setup
        if _should_start_scheduler():
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception:
                # We must not crash app startup because of scheduler issues
                pass
        # Register signals
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
