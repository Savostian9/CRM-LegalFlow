
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Кастомная модель пользователя
class User(AbstractUser):
    # Дополнительные поля для наших ролей
    is_client = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True) # Делаем email уникальным

    def __str__(self):
        return self.username

# Модель для токена подтверждения email
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    # Добавляем это поле для отслеживания времени создания
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"
    
# Модель 1: Личные данные клиента
class Client(models.Model):
    # Мы УБРАЛИ поле user = models.OneToOneField(...)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    # Возвращаем unique=True, так как email теперь должен быть уникальным для каждого клиента
    email = models.EmailField(unique=True) 
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
# Модель 2: Данные по делу о легализации
class LegalCase(models.Model):
    # Определяем возможные статусы дела
    STATUS_CHOICES = [
        ('PREPARATION', 'Подготовка документов'),
        ('SUBMITTED', 'Подано'),
        ('IN_PROGRESS', 'На рассмотрении'),
        ('DECISION_POSITIVE', 'Решение положительное'),
        ('DECISION_NEGATIVE', 'Решение отрицательное'),
        ('CLOSED', 'Дело закрыто'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='legal_cases')
    submission_date = models.DateField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREPARATION')
    
    def __str__(self):
        return f"Дело для {self.client} - Статус: {self.get_status_display()}"

# Модель 3: Документы для дела
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
    # Поле для загрузки самого файла
    file = models.FileField(upload_to='client_documents/%Y/%m/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_document_type_display()} для {self.legal_case.client}"