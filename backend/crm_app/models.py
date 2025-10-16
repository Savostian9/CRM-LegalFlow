# файл: backend/crm_app/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# --- Модель Company ---
class Company(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company_logos/%Y/%m/', blank=True, null=True)
    legal_details = models.TextField(blank=True)
    address = models.TextField(blank=True)
    owner = models.OneToOneField('User', on_delete=models.CASCADE, related_name='owned_company', null=True, blank=True)
    invite_code = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Базовый тарифный план компании (пока только STARTER, позже можно добавить FREE / PRO / и т.п.)
    plan = models.CharField(max_length=30, default='TRIAL', help_text='Код активного тарифного плана')
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

ROLE_CHOICES = [
    ('ADMIN', 'Администратор'),
    ('LEAD', 'Руководитель'),
    ('LAWYER', 'Юрист/Консультант'),
    ('MANAGER', 'Менеджер'),
    ('ASSISTANT', 'Ассистент'),
]

# --- Модель User ---
class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)  # Сохранено для обратной совместимости фронта
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    is_blocked = models.BooleanField(default=False)
    # Флаг однократного «сидирования» уведомлений из уже существующих напоминаний
    reminder_notifications_seeded = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# --- Модель для токена подтверждения email ---
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"

# --- Модель Client ---
class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_profile')
    # Аккаунт, через который создан этот клиент (владелец/менеджер аккаунта)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_clients', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    address = models.TextField(blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    passport_expiry_date = models.DateField('Срок действия паспорта', null=True, blank=True)
    visa_type = models.CharField('Тип визы', max_length=50, blank=True)
    visa_expiry_date = models.DateField('Срок действия визы', null=True, blank=True)
    notes = models.TextField('Заметки', blank=True, default='')
    # Финансы
    service_cost = models.DecimalField('Стоимость услуги', max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField('Оплачено', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def balance(self):
        try:
            return (self.service_cost or 0) - (self.amount_paid or 0)
        except Exception:
            return 0

# --- Модель LegalCase ---
class LegalCase(models.Model):
    STATUS_CHOICES = [
        ('-', '-'),
        ('PREPARATION', 'Подготовка документов'),
        ('SUBMITTED', 'Подано'),
        ('IN_PROGRESS', 'На рассмотрении'),
        ('DECISION_POSITIVE', 'Решение положительное'),
        ('DECISION_NEGATIVE', 'Решение отрицательное'),
        ('CLOSED', 'Дело закрыто'),
    ]
    CASE_TYPE_CHOICES = [
        ('-', ' -'),
        ('CZASOWY_POBYT', 'ВНЖ (Карта временного побыту)'),
        ('STALY_POBYT', 'ПМЖ (Карта сталего побыту)'),
        ('REZydent_UE', 'Карта резидента ЕС'),
        ('OBYWATELSTWO', 'Гражданство'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='legal_cases')
    case_type = models.CharField('Вид дела', max_length=20, choices=CASE_TYPE_CHOICES, default='CZASOWY_POBYT')
    submission_date = models.DateField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREPARATION')

    def __str__(self):
        return f"{self.get_case_type_display()} для {self.client}"

# --- Модель Document ---
class Document(models.Model):
    DOCUMENT_TYPES = [
        ('ZALACZNIK_1', 'Załącznik nr 1'),
        ('UMOWA_PRACA', 'Umowa o pracę / zlecenia'),
        ('UMOWA_NAJMU', 'Umowa najmu'),
        ('ZUS_ZUA_ZZA', 'ZUS ZUA / ZZA'),
        ('ZUS_RCA_DRA', 'ZUS RCA/DRA'),
        ('POLISA', 'Polisa ubezpieczeniowa'),
        ('ZASWIADCZENIE_US', 'Zaświadczenie z Urzędu Skarbowego'),
        ('ZASWIADCZENIA_ZUS', 'Zaświadczenia ZUS pracodawcy'),
        ('PIT_37', 'PIT 37'),
        ('BADANIE_LEKARSKIE', 'Badanie lekarskie'),
        ('BADANIE_MEDYCZNE', 'Badanie medyczne'),
        ('SWIADECTWO_KIEROWCY', 'Świadectwo kierowcy'),
        ('PRAWO_JAZDY', 'Prawo jazdy'),
        ('INNE', 'Inne'),
    ]
    STATUS_CHOICES = [
        ('NOT_SUBMITTED', 'Не подан'),
        ('SUBMITTED', 'Подан'),
        ('APPROVED', 'Принят'),
        ('REJECTED', 'Отклонен'),
    ]

    legal_case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_SUBMITTED')

    class Meta:
        unique_together = ('legal_case', 'document_type')
        
    def __str__(self):
        return f"{self.get_document_type_display()} для {self.legal_case.client}"

# --- Модель UploadedFile ---
class UploadedFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='client_documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.file.name

# --- Модель Task (для календаря) ---
class Task(models.Model):
    # Убираем обязательный тип задачи: оставляем список для обратной совместимости, но поле станет необязательным
    TASK_TYPES = [
        ('CALL', 'Звонок'),
        ('MEETING', 'Встреча'),
        ('SUBMISSION', 'Подача документов'),
    ]
    STATUS_CHOICES = [
        ('SCHEDULED', 'Запланировано'),
        ('DONE', 'Выполнено'),
        ('CANCELLED', 'Отменено'),
    ]
    RECURRENCE_CHOICES = [
        ('NONE', 'Нет'),
        ('DAILY', 'Ежедневно'),
        ('WEEKLY', 'Еженедельно'),
        ('MONTHLY', 'Ежемесячно'),
    ]

    # Клиент теперь опционален: задача может быть без привязки к конкретному клиенту
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    # Создатель задачи (для личных задач без клиента и разграничения доступа)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    title = models.CharField(max_length=200, blank=True)
    # task_type теперь НЕобязателен (может быть пустым)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    reminder_minutes = models.IntegerField(null=True, blank=True)
    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks', blank=True)
    location = models.CharField(max_length=255, blank=True)
    video_link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='NONE')
    recurrence_days = models.CharField(max_length=50, blank=True, help_text='Дни недели для еженедельного, например 1,3,5')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['start']),
            models.Index(fields=['end']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        try:
            base = self.get_task_type_display()
        except Exception:
            base = ''
        label = base or self.title or 'Задача'
        return f"{label} ({self.start} - {self.end})"

    @property
    def balance_safe_tz(self):
        # пример свойства, если понадобится конвертация
        return timezone.localtime(self.start)

# --- Модель Reminder (напоминания клиенту по email) ---
class Reminder(models.Model):
    REMINDER_TYPES = [
        ('UMOWA_PRACA_ZLECENIA', 'Umowa o pracę / zlecenia'),
        ('UMOWA_NAJMU', 'Umowa najmu'),
        ('ZUS_ZUA_ZZA', 'ZUS ZUA / ZZA'),
        ('ZUS_RCA_DRA', 'ZUS RCA/DRA'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=30, choices=REMINDER_TYPES)
    reminder_date = models.DateField(null=True, blank=True, help_text='Дата, когда отправить напоминание')
    reminder_time = models.TimeField(null=True, blank=True, help_text='Время в день напоминания')
    sent_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('client', 'reminder_type')
        indexes = [
            models.Index(fields=['reminder_date']),
            models.Index(fields=['reminder_type']),
            models.Index(fields=['reminder_time']),
        ]

    def __str__(self):
        return f"{self.get_reminder_type_display()} → {self.client} (на {self.reminder_date} {self.reminder_time or ''})"

# --- Приглашение в компанию ---
class Invite(models.Model):
    token = models.CharField(max_length=64, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invites')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='LAWYER')
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_invites')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite {self.token[:8]}… to {self.company} as {self.role}"

# --- Уведомление (для менеджера/пользователя) ---
class Notification(models.Model):
    SOURCE_CHOICES = [
        ('REMINDER', 'Напоминание'),
        ('SYSTEM', 'Система'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    # Optional link to a Task this notification refers to (for filtering and UI linking)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    reminder = models.ForeignKey(Reminder, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=30, blank=True, choices=SOURCE_CHOICES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Когда уведомление должно стать видимым (для отложенных напоминаний)
    visible_at = models.DateTimeField(null=True, blank=True, help_text='Если задано — показывать начиная с этого времени')
    # Плановое время (копия вычисленного времени напоминания для аналитики)
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text='Запланированное время события (из напоминания)')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['source']),
            models.Index(fields=['visible_at']),
            models.Index(fields=['task']),
        ]

    def __str__(self):
        return f"[{self.source}] {self.title} -> {self.user}" 