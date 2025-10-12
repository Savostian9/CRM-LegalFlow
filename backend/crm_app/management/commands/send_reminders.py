from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from crm_app.models import Reminder, Notification, User


class Command(BaseCommand):
    help = 'Send email reminders for reminders scheduled for today at the specified time (if any) and not yet sent.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        qs = Reminder.objects.select_related('client').filter(reminder_date=today, sent_at__isnull=True)
        self.stdout.write(f'Due reminders (today) found: {qs.count()}')
        sent = 0
        for rem in qs:
            client = rem.client
            to_email = client.email
            if not to_email:
                continue
            # Проверяем время, если оно задано: отправляем только если наступило
            if rem.reminder_time and now.time() < rem.reminder_time:
                continue
            subject = 'Przypomnienie o wygasającym dokumencie'
            doc_name = rem.get_reminder_type_display()
            message = (
                f"Dzień dobry, {client.first_name} {client.last_name},\n\n"
                f"Przypomnienie: zbliża się termin ważności dokumentu: {doc_name}.\n"
                f"Data przypomnienia: {today}{(' ' + rem.reminder_time.strftime('%H:%M')) if rem.reminder_time else ''}.\n"
                f"{rem.note or ''}\n\n"
                f"Pozdrawiamy,\nCRM LegalFlow"
            )
            email_ok = True
            try:
                self.stdout.write(f"Sending reminder #{rem.id} to client #{client.id} <{to_email}>")
                send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [to_email], fail_silently=False)
            except Exception as e:
                email_ok = False
                self.stderr.write(f"Failed to send reminder #{rem.id} to {to_email}: {e}")
            # Создаём уведомления (всегда, даже если письмо не ушло)
            try:
                # Выбираем компанию клиента (по created_by либо по связанному user)
                company_id = None
                try:
                    if getattr(client, 'created_by', None) and client.created_by.company_id:
                        company_id = client.created_by.company_id
                    elif getattr(client, 'user', None) and client.user.company_id:
                        company_id = client.user.company_id
                except Exception:
                    company_id = None

                # Рассылка уведомлений ВСЕМ внутренним сотрудникам компании клиента.
                # Предыдущая логика отправляла только одному менеджеру => пользователи "не видят" новые уведомления.
                staff = []
                try:
                    company = None
                    # 1) company через created_by
                    if getattr(client, 'created_by', None) and client.created_by.company_id:
                        company = client.created_by.company
                    # 2) иначе через связанный user (клиентский аккаунт)
                    if not company and getattr(client, 'user', None) and client.user.company_id:
                        company = client.user.company
                    if company:
                        staff_qs = company.users.filter(is_client=False)
                        # опциональный фильтр по ролям
                        staff = list(staff_qs)
                except Exception:
                    staff = []
                # Fallback: если никого не нашли, хотя бы created_by
                if not staff and getattr(client, 'created_by', None):
                    staff = [client.created_by]
                # Ещё fallback: любой пользователь (owner)
                if not staff:
                    try:
                        if company:
                            owner = getattr(company, 'owner', None)
                            if owner:
                                staff = [owner]
                    except Exception:
                        pass

                status_note = 'отправлено' if email_ok else 'ОШИБКА отправки email'
                title = f"Напоминание: {doc_name} ({status_note})"
                msg_preview = f"Клиент: {client.first_name} {client.last_name} ({client.email})"
                scheduled_dt = timezone.make_aware(timezone.datetime.combine(rem.reminder_date, rem.reminder_time)) if rem.reminder_date else now

                for u in staff:
                    if not u:
                        continue
                    Notification.objects.get_or_create(
                        user=u,
                        reminder=rem,
                        defaults={
                            'client': client,
                            'title': title[:200],
                            'message': msg_preview,
                            'source': 'REMINDER',
                            'visible_at': now if scheduled_dt <= now else scheduled_dt,
                            'scheduled_for': scheduled_dt,
                        }
                    )
            except Exception:
                self.stderr.write(f"Failed to create staff notifications for reminder #{rem.id}")
            rem.sent_at = timezone.now()
            rem.save(update_fields=['sent_at'])
            if email_ok:
                sent += 1
        self.stdout.write(self.style.SUCCESS(f'Sent reminders: {sent}'))
