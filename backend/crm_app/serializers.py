# файл: backend/crm_app/serializers.py

from rest_framework import serializers
from .models import User, Client
from .models import Client, LegalCase, Document
from django.utils.crypto import get_random_string

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_client', 'is_manager', 'is_admin']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Пароль будет только для записи

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,  # <-- САМОЕ ГЛАВНОЕ ИЗМЕНЕНИЕ
            is_client=True
        )
        return user
    
class ClientListSerializer(serializers.ModelSerializer):
    # Дополнительные поля, которых нет в модели, но мы их вычислим
    active_case_status = serializers.SerializerMethodField()
    active_case_status_class = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'active_case_status', 'active_case_status_class']

    def get_active_case_status(self, obj):
        # Находим последнее (самое новое) дело клиента
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.get_status_display() if active_case else 'Нет дел'

    def get_active_case_status_class(self, obj):
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.status.lower() if active_case else 'no-case'
    
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        # Указываем поля, которые приходят из формы
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'address']

# Сериализатор для документов
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'status', 'file']

class LegalCaseSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LegalCase
        # УБИРАЕМ 'client' из полей, чтобы не было рекурсии
        fields = ['id', 'submission_date', 'decision_date', 'status', 'status_display', 'documents']

class ClientSerializer(serializers.ModelSerializer):
    legal_cases = LegalCaseSerializer(many=True)

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 
            'phone_number', 'address', 'legal_cases'
        ]

    def update(self, instance, validated_data):
        # Обновляем данные самого клиента
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        cases_data = validated_data.get('legal_cases', [])
        
        if cases_data:
            case_data = cases_data[0]
            documents_data = case_data.pop('documents', [])
            
            # Обновляем или создаем дело
            legal_case, created = LegalCase.objects.update_or_create(
                client=instance, defaults=case_data
            )

            # Обновляем документы для этого дела
            for document_data in documents_data:
                Document.objects.update_or_create(
                    legal_case=legal_case,
                    document_type=document_data['document_type'],
                    defaults=document_data
                )

        return instance