# файл: backend/crm_app/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# --- Модель User ---
class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    passport_expiry_date = models.DateField('Срок действия паспорта', null=True, blank=True)
    visa_type = models.CharField('Тип визы', max_length=50, blank=True)
    visa_expiry_date = models.DateField('Срок действия визы', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# --- Модель LegalCase ---
class LegalCase(models.Model):
    STATUS_CHOICES = [
        ('PREPARATION', 'Подготовка документов'),
        ('SUBMITTED', 'Подано'),
        ('IN_PROGRESS', 'На рассмотрении'),
        ('DECISION_POSITIVE', 'Решение положительное'),
        ('DECISION_NEGATIVE', 'Решение отрицательное'),
        ('CLOSED', 'Дело закрыто'),
    ]
    CASE_TYPE_CHOICES = [
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