from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from crm_app.models import Company, Client, Task, LegalCase, Document, UploadedFile, PLAN_LIMITS
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

User = get_user_model()

class PlanLimitsTests(TestCase):
    def setUp(self):
        # 1. Создаем компанию с тарифом TRIAL
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.company = Company.objects.create(name='Test Company', owner=self.user, plan='TRIAL')
        self.user.company = self.company
        self.user.role = 'ADMIN'
        self.user.save()
        
        # 2. Настраиваем клиент API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Получаем лимиты для Trial
        self.limits = PLAN_LIMITS['TRIAL']

    def test_client_creation_limit(self):
        """Тест: Нельзя создать больше клиентов, чем в лимите"""
        limit = self.limits['clients']
        
        # Создаем максимально разрешенное количество клиентов напрямую в БД
        for i in range(limit):
            u = User.objects.create_user(username=f'client{i}', email=f'client{i}@example.com', password='password')
            Client.objects.create(
                created_by=self.user, 
                user=u,
                first_name=f"Client {i}", 
                last_name="Test",
                email=f"test{i}@example.com",
                phone_number="123",
                address="addr",
                passport_number="123",
                visa_type="type",
                service_cost=0,
                amount_paid=0,
                notes=""
            )

        # Пытаемся создать (limit + 1)-го клиента через API
        data = {
            "first_name": "Extra",
            "last_name": "Client",
            "email": "extra@example.com",
            "phone_number": "123456",
        }
        response = self.client.post('/api/clients/', data)

        # Ожидаем ошибку 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем, что в ответе есть сообщение о лимите (ключ detail или общий текст)
        self.assertTrue('detail' in response.data or 'error' in response.data)
        error_msg = str(response.data)
        self.assertIn("Превышен лимит", error_msg)

    def test_task_creation_limit(self):
        """Тест: Нельзя создать больше задач, чем в лимите"""
        limit = self.limits['tasks_per_month']
        
        # Создаем фиктивного клиента
        u = User.objects.create_user(username='client_task', email='client_task@example.com', password='password')
        client = Client.objects.create(
            created_by=self.user, 
            user=u,
            first_name="C", 
            last_name="L", 
            email="c@l.com",
            phone_number="123",
            address="addr",
            passport_number="123",
            visa_type="type",
            service_cost=0,
            amount_paid=0,
            notes=""
        )

        # Заполняем лимит задач
        now = timezone.now()
        tasks = [
            Task(created_by=self.user, title=f"Task {i}", client=client, status='SCHEDULED', start=now, end=now)
            for i in range(limit)
        ]
        Task.objects.bulk_create(tasks)

        # Пытаемся создать лишнюю задачу
        data = {
            "title": "Extra Task",
            "client_id": client.id,
            "status": "SCHEDULED",
            "start": now.isoformat(),
            "end": now.isoformat()
        }
        response = self.client.post('/api/tasks/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Превышен лимит", str(response.data))

    def test_case_creation_limit(self):
        """Тест: Нельзя создать больше дел, чем в лимите"""
        limit = self.limits['cases']
        
        u = User.objects.create_user(username='client_case', email='client_case@example.com', password='password')
        client = Client.objects.create(
            created_by=self.user, 
            user=u,
            first_name="C", 
            last_name="L", 
            email="c@l.com",
            phone_number="123",
            address="addr",
            passport_number="123",
            visa_type="type",
            service_cost=0,
            amount_paid=0,
            notes=""
        )

        # Заполняем лимит дел
        cases = [
            LegalCase(client=client, case_type='CZASOWY_POBYT', status='PREPARATION')
            for i in range(limit)
        ]
        LegalCase.objects.bulk_create(cases)

        # Пытаемся создать лишнее дело
        data = {
            "case_type": "CZASOWY_POBYT",
            "status": "PREPARATION"
        }
        response = self.client.post(f'/api/clients/{client.id}/cases/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Превышен лимит", str(response.data))

    def test_storage_limit(self):
        """Тест: Нельзя загрузить файл, если превышен объем хранилища"""
        limit_mb = self.limits['files_storage_mb']
        
        u = User.objects.create_user(username='client_file', email='client_file@example.com', password='password')
        client = Client.objects.create(
            created_by=self.user, 
            user=u,
            first_name="C", 
            last_name="L", 
            email="c@l.com",
            phone_number="123",
            address="addr",
            passport_number="123",
            visa_type="type",
            service_cost=0,
            amount_paid=0,
            notes=""
        )
        legal_case = LegalCase.objects.create(client=client, case_type='CZASOWY_POBYT', status='PREPARATION')
        document = Document.objects.create(legal_case=legal_case, name="Doc", document_type='INNE', status='NOT_SUBMITTED')
        
        # Создаем фиктивный файл в БД, который "занимает" всё место
        UploadedFile.objects.create(
            document=document,
            file="dummy.pdf",
            file_size=limit_mb * 1024 * 1024  # Забиваем всё место
        )

        # Пытаемся загрузить маленький файл через API
        file_content = b"small content"
        test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        
        data = {
            "file": test_file,
            "description": "Test file"
        }
        
        # Правильный URL: /api/documents/<id>/files/
        response = self.client.post(f'/api/documents/{document.id}/files/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Превышен лимит", str(response.data))
