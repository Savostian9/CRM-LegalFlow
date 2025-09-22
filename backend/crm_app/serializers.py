# файл: backend/crm_app/serializers.py

from rest_framework import serializers
from .models import User, Client, LegalCase, Document, UploadedFile

# --- СЕРИАЛИЗАТОРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
            is_client=True
        )
        return user

# --- СЕРИАЛИЗАТОРЫ ДЛЯ КЛИЕНТОВ И ДЕЛ ---

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'description', 'uploaded_at']

class DocumentSerializer(serializers.ModelSerializer):
    files = UploadedFileSerializer(many=True, read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'status', 'document_type_display', 'files']

# файл: backend/crm_app/serializers.py

class LegalCaseSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Добавляем новое поле для отображения
    case_type_display = serializers.CharField(source='get_case_type_display', read_only=True)

    class Meta:
        model = LegalCase
        # Добавляем новые поля в список
        fields = ['id', 'case_type', 'case_type_display', 'submission_date', 'decision_date', 'status', 'status_display', 'documents']
        
# --- ЕДИНЫЙ И ПРАВИЛЬНЫЙ ClientSerializer ---
class ClientSerializer(serializers.ModelSerializer):
    legal_cases = LegalCaseSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'address',
            'passport_number', 'passport_expiry_date', 'visa_type',
            'visa_expiry_date', 'legal_cases'
        ]

    def create(self, validated_data):
        validated_data.pop('legal_cases', None)
        user, created = User.objects.get_or_create(
            email=validated_data['email'],
            defaults={'username': validated_data['email'], 'is_active': False, 'is_client': True}
        )
        client = Client.objects.create(user=user, **validated_data)
        return client

    def update(self, instance, validated_data):
        cases_data = validated_data.pop('legal_cases', [])
        
        # Обновляем поля самого клиента
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.passport_number = validated_data.get('passport_number', instance.passport_number)
        instance.passport_expiry_date = validated_data.get('passport_expiry_date', instance.passport_expiry_date)
        instance.visa_type = validated_data.get('visa_type', instance.visa_type)
        instance.visa_expiry_date = validated_data.get('visa_expiry_date', instance.visa_expiry_date)
        instance.save()

        if cases_data:
            case_data = cases_data[0]
            documents_data = case_data.pop('documents', [])
            
            legal_case, created = LegalCase.objects.update_or_create(
                client=instance, defaults=case_data
            )

            sent_doc_ids = {item.get('id') for item in documents_data if item.get('id')}
            for doc in legal_case.documents.all():
                if doc.id not in sent_doc_ids:
                    doc.delete()

            for document_data in documents_data:
                doc_id = document_data.get('id', None)
                if doc_id:
                    Document.objects.filter(id=doc_id, legal_case=legal_case).update(**document_data)
                else:
                    Document.objects.create(legal_case=legal_case, **document_data)

        return instance

# --- СЕРИАЛИЗАТОР ДЛЯ СПИСКА КЛИЕНТОВ ---
class ClientListSerializer(serializers.ModelSerializer):
    active_case_status = serializers.SerializerMethodField()
    active_case_status_class = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'active_case_status', 'active_case_status_class']

    def get_active_case_status(self, obj):
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.get_status_display() if active_case else 'Нет дел'

    def get_active_case_status_class(self, obj):
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.status.lower() if active_case else 'no-case'