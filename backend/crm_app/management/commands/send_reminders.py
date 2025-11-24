from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from crm_app.models import Reminder, Notification, User
from django.db import transaction
from django.db.models import Q
from crm_app.limits import check_limit
from rest_framework.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Send email reminders for reminders scheduled for today at the specified time (if any) and not yet sent.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        qs = (
            Reminder.objects.select_related('client')
            .filter(sent_at__isnull=True)
            .filter(
                Q(reminder_date__lt=today)
                | Q(reminder_date=today, reminder_time__isnull=True)
                | Q(reminder_date=today, reminder_time__lte=now.time())
            )
        )
        self.stdout.write(f'Due reminders (<= now) found: {qs.count()}')
        sent = 0
        for rem in qs:
            client = rem.client
            to_email = (getattr(client, 'email', '') or '').strip()
            # Проверяем время, если оно задано: отправляем только если наступило
            # В выборке уже учтено время; дополнительная проверка не нужна
            # Идемпотентность: атомарно "забронируем" напоминание, чтобы в параллельных процессах не отправить дубликаты
            claimed = Reminder.objects.filter(pk=rem.pk, sent_at__isnull=True).update(sent_at=timezone.now())
            if not claimed:
                # Уже взято/отправлено другим процессом
                continue

            # Проверка лимитов перед отправкой
            owner = client.created_by or client.user
            limit_error = None
            try:
                if owner:
                    check_limit(owner, 'emails_per_month')
            except ValidationError as e:
                limit_error = e.detail if isinstance(e.detail, str) else str(e)
                if isinstance(e.detail, dict) and 'detail' in e.detail:
                    limit_error = e.detail['detail']

            subject = 'Напоминание / Przypomnienie o wygasającym dokumencie'
            doc_name = rem.get_reminder_type_display()
            message = (
                f"Здравствуйте, {client.first_name} {client.last_name}!\n\n"
                f"Напоминание: приближается срок действия документа: {doc_name}.\n"
                f"Дата напоминания: {today}{(' ' + rem.reminder_time.strftime('%H:%M')) if rem.reminder_time else ''}.\n"
                f"{rem.note or ''}\n\n"
                f"С уважением,\nCRM LegalFlow\n\n"
                f"------------------------------------------------------------\n\n"
                f"Dzień dobry, {client.first_name} {client.last_name},\n\n"
                f"Przypomnienie: zbliża się termin ważności dokumentu: {doc_name}.\n"
                f"Data przypomnienia: {today}{(' ' + rem.reminder_time.strftime('%H:%M')) if rem.reminder_time else ''}.\n"
                f"{rem.note or ''}\n\n"
                f"Pozdrawiamy,\nCRM LegalFlow"
            )
            email_ok = False
            send_error = None

            if limit_error:
                send_error = 'limit_reached'
                self.stdout.write(f"Limit reached for reminder #{rem.id}: {limit_error}")
            elif to_email:
                try:
                    self.stdout.write(f"Sending reminder #{rem.id} to client #{client.id} <{to_email}>")
                    send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [to_email], fail_silently=False)
                    email_ok = True

                    # Log SentEmail for billing
                    try:
                        from crm_app.models import SentEmail
                        company = getattr(owner, 'company', None) if owner else None
                        SentEmail.objects.create(
                            user=owner,
                            company=company,
                            recipient=to_email,
                            subject=subject
                        )
                    except Exception as e:
                        self.stderr.write(f"Failed to log SentEmail: {e}")

                except Exception as e:
                    send_error = str(e)
                    self.stderr.write(f"Failed to send reminder #{rem.id} to {to_email}: {e}")
            else:
                send_error = 'no_client_email'
                self.stderr.write(f"Reminder #{rem.id}: client #{client.id} has no email; creating staff notification only")

            # Создаём уведомления ТОЛЬКО ответственному менеджеру (client.created_by)
            try:
                company = None
                if getattr(client, 'created_by', None) and getattr(client.created_by, 'company_id', None):
                    company = client.created_by.company
                elif getattr(client, 'user', None) and getattr(client.user, 'company_id', None):
                    company = client.user.company

                recipients = []
                primary = getattr(client, 'created_by', None)
                if primary:
                    recipients = [primary]

                if recipients:
                    if email_ok:
                        status_note = 'отправлено'
                        source_type = 'REMINDER'
                    elif send_error == 'limit_reached':
                        status_note = 'лимит исчерпан, не отправлено'
                        source_type = 'SYSTEM' # Не считаем как отправленное напоминание
                    elif send_error == 'no_client_email':
                        status_note = 'нет email у клиента'
                        source_type = 'SYSTEM'
                    else:
                        status_note = 'ОШИБКА отправки email'
                        source_type = 'SYSTEM'

                    title = f"Напоминание: {doc_name} ({status_note})"
                    msg_preview = f"Клиент: {client.first_name} {client.last_name} ({client.email})"
                    if limit_error:
                        msg_preview += f"\n\nПричина: {limit_error}"
                    
                    try:
                        base_time = rem.reminder_time or timezone.datetime.min.time()
                        scheduled_dt = timezone.make_aware(
                            timezone.datetime.combine(rem.reminder_date, base_time),
                            timezone.get_current_timezone()
                        ) if rem.reminder_date else now
                    except Exception:
                        scheduled_dt = now
                    for r in recipients:
                        try:
                            Notification.objects.create(
                                user=r,
                                reminder=rem,
                                client=client,
                                title=title[:200],
                                message=msg_preview,
                                source=source_type,
                                visible_at=now,
                                scheduled_for=scheduled_dt,
                            )
                        except Exception:
                            continue
            except Exception:
                self.stderr.write(f"Failed to create notification(s) for reminder #{rem.id}")

            # Если отправка успешна — увеличиваем счетчик
            if email_ok:
                sent += 1
            # ВАЖНО: Мы НЕ сбрасываем sent_at в None при ошибке, чтобы избежать бесконечного цикла.
            # Напоминание считается обработанным (либо отправлено, либо ошибка/лимит).
            
        self.stdout.write(self.style.SUCCESS(f'Sent reminders: {sent}'))