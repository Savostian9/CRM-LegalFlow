from django.utils import timezone
from django.utils.translation import get_language
from django.db.models import Sum, Q
from rest_framework.exceptions import ValidationError
from .models import PLAN_LIMITS, User, Client, LegalCase, Document, UploadedFile, Task, Notification

def check_limit(user, resource_key):
    """
    Проверяет, не превышен ли лимит для указанного ресурса.
    Если превышен — выбрасывает ValidationError.
    """
    if not user or not user.company:
        # Если пользователь не привязан к компании, лимиты не проверяем (или считаем безлимитом)
        return
    
    company = user.company
    plan = company.plan or 'TRIAL'
    
    # Если план не найден в каталоге, берем TRIAL как дефолт
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['TRIAL'])
    limit = limits.get(resource_key)
    
    # Если лимит не задан или None — считаем безлимитом
    if limit is None:
        return

    current_usage = 0
    
    if resource_key == 'users':
        # Считаем только реальных пользователей (без приглашений)
        current_usage = company.users.count()
        
    elif resource_key == 'clients':
        # Клиенты, созданные сотрудниками компании или привязанные к компании
        current_usage = Client.objects.filter(
            Q(created_by__company=company) | Q(user__company=company)
        ).distinct().count()
        
    elif resource_key == 'cases':
        # Дела клиентов компании (созданных сотрудниками или привязанных)
        current_usage = LegalCase.objects.filter(
            Q(client__created_by__company=company) | Q(client__user__company=company)
        ).distinct().count()
        
    elif resource_key == 'files':
        # Файлы, привязанные к документам дел клиентов компании
        current_usage = UploadedFile.objects.filter(
            Q(document__legal_case__client__created_by__company=company) | 
            Q(document__legal_case__client__user__company=company)
        ).distinct().count()

    elif resource_key == 'files_storage_mb':
        # Суммарный размер файлов в МБ
        total_bytes = UploadedFile.objects.filter(
            Q(document__legal_case__client__created_by__company=company) | 
            Q(document__legal_case__client__user__company=company)
        ).distinct().aggregate(Sum('file_size'))['file_size__sum'] or 0
        current_usage = total_bytes / (1024 * 1024)

    elif resource_key == 'tasks_per_month':
        # Задачи, созданные сотрудниками компании в текущем месяце
        now = timezone.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_usage = Task.objects.filter(
            Q(client__in=Client.objects.filter(
                Q(created_by__company=company) | Q(user__company=company)
            )) |
            Q(created_by__company=company),
            created_at__gte=start_month
        ).distinct().count()

    elif resource_key == 'emails_per_month':
        # Уведомления (напоминания), отправленные в текущем месяце
        # Используем SentEmail для более точного подсчета отправленных писем
        from .models import SentEmail
        now = timezone.now()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_usage = SentEmail.objects.filter(
            company=company,
            sent_at__gte=start_month
        ).count()

    # Проверка
    if current_usage >= limit:
        resource_names_ru = {
            'users': 'пользователи',
            'clients': 'клиенты',
            'cases': 'дела',
            'files': 'файлы',
            'files_storage_mb': 'хранилище (МБ)',
            'tasks_per_month': 'задачи',
            'emails_per_month': 'email напоминания',
        }
        resource_names_pl = {
            'users': 'użytkownicy',
            'clients': 'klienci',
            'cases': 'sprawy',
            'files': 'pliki',
            'files_storage_mb': 'pamięć (MB)',
            'tasks_per_month': 'zadania',
            'emails_per_month': 'email przypomnień',
        }

        lang = get_language()
        if lang and lang.lower().startswith('pl'):
            res_pl = resource_names_pl.get(resource_key, resource_key)
            msg = f'Przekroczono limit planu "{plan}" dla zasobu "{res_pl}". Obecnie: {int(current_usage)}, Limit: {limit}. Zaktualizuj plan.'
        else:
            res_ru = resource_names_ru.get(resource_key, resource_key)
            msg = f'Превышен лимит тарифного плана "{plan}" по ресурсу "{res_ru}". Текущее: {int(current_usage)}, Лимит: {limit}. Обновите тариф.'
        
        raise ValidationError({
            'detail': msg
        })
