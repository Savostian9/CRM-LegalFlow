# файл: backend/crm_app/serializers.py

from rest_framework import serializers
from django.db import models
from django.contrib.auth import authenticate
from .models import User, Client, LegalCase, Document, UploadedFile, Task, Reminder, Company, Invite, Notification, UserPermissionSet
from .limits import check_limit

# --- СЕРИАЛИЗАТОРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ---
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Переопределяем поля, чтобы задать русские сообщения об ошибках
    username = serializers.CharField(
        error_messages={
            'blank': 'Имя пользователя обязательно.',
            'required': 'Имя пользователя обязательно.',
            'invalid': 'Введите корректное имя пользователя.'
        }
    )
    email = serializers.EmailField(
        error_messages={
            'blank': 'Email обязателен.',
            'required': 'Email обязателен.',
            'invalid': 'Введите корректный email.'
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            'blank': 'Пароль обязателен.',
            'required': 'Пароль обязателен.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        import re
        value = (value or '').strip().lower()
        # Разрешенный набор по умолчанию Django: латиница/цифры/ @ . + - _
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Введите корректное имя пользователя. Допустимы буквы, цифры и символы @/./+/-/_ .')
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value

    def validate_email(self, value):
        # Считаем email уникальным без учета регистра
        value = (value or '').strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def create(self, validated_data):
        # Нормализуем вход для надежности
        validated_data['username'] = (validated_data.get('username') or '').strip().lower()
        validated_data['email'] = (validated_data.get('email') or '').strip().lower()
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
            is_client=False,
            is_manager=True
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'avatar']
        read_only_fields = ['id', 'email']

    def validate_username(self, value):
        import re
        value = (value or '').strip().lower()
        if not value:
            raise serializers.ValidationError('Имя пользователя обязательно.')
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Введите корректное имя пользователя. Допустимы буквы, цифры и символы @/./+/-/_ .')
        # Уникальность с исключением текущего пользователя
        qs = User.objects.filter(username__iexact=value)
        user = self.instance if isinstance(self.instance, User) else None
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return value

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'legal_details', 'address', 'logo', 'invite_code']
        read_only_fields = ['invite_code', 'id']

class UserAdminSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_blocked', 'is_owner']

    def get_is_owner(self, obj):
        try:
            return getattr(obj.company, 'owner_id', None) == obj.id
        except Exception:
            return False


class UserPermissionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissionSet
        fields = [
            'can_create_client', 'can_edit_client', 'can_delete_client',
            'can_create_case', 'can_edit_case', 'can_delete_case',
            'can_create_task', 'can_edit_task', 'can_delete_task',
            'can_upload_files', 'can_invite_users', 'can_manage_users',
            'updated_at'
        ]


class InviteSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    class Meta:
        model = Invite
        fields = ['token', 'company', 'company_name', 'role', 'is_active', 'expires_at', 'created_at']

# --- СЕРИАЛИЗАТОР ДЛЯ ВХОДА ПО EMAIL ---
class EmailAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        # Нормализуем регистр
        email = (attrs.get('email') or '').strip().lower() or None
        username = (attrs.get('username') or '').strip().lower() or None
        password = attrs.get('password')

        if (not email and not username) or not password:
            raise serializers.ValidationError('Укажите email или имя пользователя и пароль.')

        user_obj = None
        if email:
            try:
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                pass
        if user_obj is None and username:
            try:
                user_obj = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                pass
        if user_obj is None:
            raise serializers.ValidationError('Неверные учетные данные.')

        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError('Неверные учетные данные.')
        if not user.is_active:
            raise serializers.ValidationError('Учетная запись не активирована.')

        attrs['user'] = user
        return attrs

# --- СЕРИАЛИЗАТОРЫ ДЛЯ КЛИЕНТОВ И ДЕЛ ---

class UploadedFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'description', 'uploaded_at']

    def get_file(self, obj):
        if not obj.file:
            return None
        try:
            # Determine disposition based on extension
            name = obj.file.name.lower()
            disposition = 'attachment'
            if name.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.webp')):
                disposition = 'inline'
            
            # Force content disposition for signed URLs (S3)
            return obj.file.storage.url(obj.file.name, parameters={'ResponseContentDisposition': disposition})
        except TypeError:
            # Fallback for storage backends that don't support parameters (e.g. FileSystemStorage)
            return obj.file.url
        except Exception:
            return obj.file.url

class DocumentSerializer(serializers.ModelSerializer):
    files = UploadedFileSerializer(many=True, read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'document_type', 'name', 'status', 'document_type_display', 'files']

class ReminderSerializer(serializers.ModelSerializer):
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)

    class Meta:
        model = Reminder
        fields = ['id', 'reminder_type', 'reminder_type_display', 'reminder_date', 'reminder_time', 'sent_at', 'note']

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
    balance = serializers.SerializerMethodField(read_only=True)
    reminders = ReminderSerializer(many=True, required=False)

    class Meta:
        model = Client
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'address',
            'passport_number', 'passport_expiry_date', 'visa_type', 'visa_expiry_date',
            'notes',
            'service_cost', 'amount_paid', 'balance',
            'legal_cases', 'reminders', 'created_at'
        ]

    def create(self, validated_data):
        validated_data.pop('legal_cases', None)
        reminders_data = validated_data.pop('reminders', None)
        base_email = (validated_data['email'] or '').strip().lower()
        # Ищем пользователя с таким email
        try:
            existing_user = User.objects.get(email__iexact=base_email)
        except User.DoesNotExist:
            existing_user = None

        if existing_user and hasattr(existing_user, 'client_profile'):
            # Если уже есть клиент, создаем отдельного пользователя с вариацией username, email оставляем тот же
            # Username должен быть уникален; email у User уникальный по модели, поэтому создадим уникальный email-алиас
            # Чтобы не ломать ограничение unique=True на User.email, добавим суффикс к локальной части
            local, at, domain = base_email.partition('@')
            idx = 2
            new_email = f"{local}+{idx}@{domain}" if at else f"{base_email}.{idx}"
            while User.objects.filter(email__iexact=new_email).exists():
                idx += 1
                new_email = f"{local}+{idx}@{domain}" if at else f"{base_email}.{idx}"
            user = User.objects.create_user(
                username=new_email.lower(),
                email=new_email.lower(),
                password=None,
                is_active=False,
                is_client=True
            )
        else:
            # Или берем существующего пользователя без клиентского профиля, или создаем нового с исходным email
            if existing_user:
                user = existing_user
            else:
                user = User.objects.create_user(
                    username=base_email.lower(),
                    email=base_email.lower(),
                    password=None,
                    is_active=False,
                    is_client=True
                )
        client = Client.objects.create(user=user, **validated_data)
        # Создаем напоминания, если были переданы при создании
        if reminders_data:
            # Проверяем лимит на количество отправленных email (если добавляем новые напоминания)
            request = self.context.get('request')
            if request and request.user:
                check_limit(request.user, 'emails_per_month')

            allowed_types = {choice[0] for choice in Reminder.REMINDER_TYPES}
            for rem in reminders_data:
                r_type = rem.get('reminder_type')
                if r_type in allowed_types:
                    Reminder.objects.update_or_create(
                        client=client,
                        reminder_type=r_type,
                        defaults={
                            'reminder_date': rem.get('reminder_date'),
                            'reminder_time': rem.get('reminder_time'),
                            'note': rem.get('note', '')
                        }
                    )
        return client

    def update(self, instance, validated_data):
        cases_data = validated_data.pop('legal_cases', [])
        reminders_data = validated_data.pop('reminders', [])
        
        # Обновляем поля самого клиента
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if 'email' in validated_data:
            instance.email = (validated_data.get('email') or '').strip().lower() or instance.email
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.service_cost = validated_data.get('service_cost', instance.service_cost)
        instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)
        instance.passport_number = validated_data.get('passport_number', instance.passport_number)
        instance.passport_expiry_date = validated_data.get('passport_expiry_date', instance.passport_expiry_date)
        instance.visa_type = validated_data.get('visa_type', instance.visa_type)
        instance.visa_expiry_date = validated_data.get('visa_expiry_date', instance.visa_expiry_date)
        instance.save()

        # Обрабатываем все дела, а не только первое
        if cases_data:
            # Получаем ID всех переданных дел
            sent_case_ids = {case_data.get('id') for case_data in cases_data if case_data.get('id')}
            
            # Удаляем дела, которых нет в переданных данных
            for existing_case in instance.legal_cases.all():
                if existing_case.id not in sent_case_ids:
                    existing_case.delete()
            
            # Обновляем или создаем дела
            for case_data in cases_data:
                case_id = case_data.get('id')
                documents_data = case_data.pop('documents', [])
                
                if case_id:
                    # Обновляем существующее дело
                    try:
                        legal_case = LegalCase.objects.get(id=case_id, client=instance)
                        for attr, value in case_data.items():
                            setattr(legal_case, attr, value)
                        legal_case.save()
                    except LegalCase.DoesNotExist:
                        continue
                else:
                    # Создаем новое дело
                    request = self.context.get('request')
                    if request and request.user:
                        check_limit(request.user, 'cases')
                    legal_case = LegalCase.objects.create(client=instance, **case_data)
                
                # Обрабатываем документы для этого дела
                if documents_data is not None:
                    sent_doc_ids = {doc_data.get('id') for doc_data in documents_data if doc_data.get('id')}
                    
                    # Удаляем документы, которых нет в переданных данных
                    for doc in legal_case.documents.all():
                        if doc.id not in sent_doc_ids:
                            doc.delete()
                    
                    # Обновляем или создаем документы
                    for document_data in documents_data:
                        # Normalize empty name to None to bypass unique collisions on blank strings
                        if 'name' in document_data and not (document_data.get('name') or '').strip():
                            document_data['name'] = None
                        doc_id = document_data.get('id')
                        if doc_id:
                            try:
                                doc = Document.objects.get(id=doc_id, legal_case=legal_case)
                                for attr, value in document_data.items():
                                    setattr(doc, attr, value)
                                doc.save()
                            except Document.DoesNotExist:
                                continue
                        else:
                            Document.objects.create(legal_case=legal_case, **document_data)

        # Обрабатываем напоминания (2 типа)
        if reminders_data:
            request = self.context.get('request')
            # Разрешенные типы
            allowed_types = {choice[0] for choice in Reminder.REMINDER_TYPES}
            provided_types = set()
            for rem in reminders_data:
                r_type = rem.get('reminder_type')
                if r_type not in allowed_types:
                    continue
                
                # Если такого напоминания нет — значит создаем новое. Проверяем лимит.
                if not Reminder.objects.filter(client=instance, reminder_type=r_type).exists():
                    if request and request.user:
                        check_limit(request.user, 'emails_per_month')

                provided_types.add(r_type)
                reminder_date = rem.get('reminder_date')
                reminder_time = rem.get('reminder_time')
                note = rem.get('note', '')
                obj, _ = Reminder.objects.get_or_create(client=instance, reminder_type=r_type)
                # Сбросить sent_at, если дату/время изменили
                if obj.reminder_date != reminder_date or obj.reminder_time != reminder_time:
                    obj.sent_at = None
                obj.reminder_date = reminder_date
                obj.reminder_time = reminder_time
                if note is not None:
                    obj.note = note
                obj.save()
            # Удаляем напоминания, не присланные (опционально). Оставим их, чтобы не терять данные.
            # Если нужно удалять отсутствующие, раскомментируйте:
            # for obj in instance.reminders.all():
            #     if obj.reminder_type not in provided_types:
            #         obj.delete()

        return instance

    def get_balance(self, obj):
        try:
            return (obj.service_cost or 0) - (obj.amount_paid or 0)
        except Exception:
            return 0

# --- СЕРИАЛИЗАТОР ДЛЯ СПИСКА КЛИЕНТОВ ---
class ClientListSerializer(serializers.ModelSerializer):
    active_case_status = serializers.SerializerMethodField()
    active_case_status_class = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.SerializerMethodField()
    created_by_first_name = serializers.SerializerMethodField()
    created_by_last_name = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'service_cost', 'amount_paid', 'balance', 'created_at',
            'created_by_name', 'created_by_id',
            'created_by_first_name', 'created_by_last_name',
            'active_case_status', 'active_case_status_class'
        ]

    def get_active_case_status(self, obj):
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.get_status_display() if active_case else 'Нет дел'

    def get_active_case_status_class(self, obj):
        active_case = obj.legal_cases.order_by('-submission_date').first()
        return active_case.status.lower() if active_case else 'no-case'

    def get_balance(self, obj):
        try:
            return (obj.service_cost or 0) - (obj.amount_paid or 0)
        except Exception:
            return 0

    def get_created_by_name(self, obj):
        try:
            u = obj.created_by
            if not u:
                return ''
            full = f"{u.first_name or ''} {u.last_name or ''}".strip()
            if full:
                return full
            # Если username не выглядит как email — покажем его, иначе email
            uname = getattr(u, 'username', '') or ''
            if uname and '@' not in uname:
                return uname
            return getattr(u, 'email', '') or uname
        except Exception:
            return ''

    def get_created_by_id(self, obj):
        try:
            return getattr(obj, 'created_by_id', None)
        except Exception:
            return None

    def get_created_by_first_name(self, obj):
        try:
            return getattr(obj.created_by, 'first_name', '') or ''
        except Exception:
            return ''

    def get_created_by_last_name(self, obj):
        try:
            return getattr(obj.created_by, 'last_name', '') or ''
        except Exception:
            return ''

# --- СЕРИАЛИЗАТОРЫ ДЛЯ КАЛЕНДАРЯ ---
class ClientLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'email']

class TaskSerializer(serializers.ModelSerializer):
    client = ClientLiteSerializer(read_only=True)
    # client_id теперь опциональное поле
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), source='client', write_only=True, required=False, allow_null=True)
    assignees = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    # Человекочитаемые имена исполнителей для фронтенда (First Last -> username -> email)
    assignees_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_type', 'start', 'end', 'all_day',
            'reminder_minutes', 'assignees', 'location', 'video_link',
            'description', 'color', 'status', 'recurrence', 'recurrence_days',
            'client', 'client_id', 'created_by', 'created_at', 'updated_at',
            'assignees_display'
        ]
        extra_kwargs = {
            'task_type': {'required': False, 'allow_blank': True},
            'title': {'required': False, 'allow_blank': True},
            'start': {'required': False},
            'end': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор клиента только клиентами, созданными текущим пользователем
        request = self.context.get('request') if isinstance(self.context, dict) else None
        if request and getattr(request, 'user', None) and 'client_id' in self.fields:
            user = request.user
            if getattr(user, 'role', None) in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and getattr(user, 'company_id', None):
                # Админские роли: клиенты всей компании
                self.fields['client_id'].queryset = Client.objects.filter(
                    models.Q(created_by__company_id=user.company_id) | models.Q(user__company_id=user.company_id)
                )
            else:
                # Менеджер: только свои клиенты
                self.fields['client_id'].queryset = Client.objects.filter(created_by=user)

    def validate(self, attrs):
        """Позволяем создавать задачу вообще без полей: если start не передан, ставим текущее время.
        end тоже автозаполняем если отсутствует. Для all_day -> end = start, иначе +1 час.
        """
        from datetime import timedelta
        from django.utils import timezone

        start = attrs.get('start')
        end = attrs.get('end')

        if not start:
            # Автозаполнение только при создании (instance еще нет); при апдейте без start оставляем старое значение
            if self.instance is None:
                start = timezone.now()
                attrs['start'] = start
        if not end:
            if start:  # если мы либо получили, либо только что выставили start
                if attrs.get('all_day'):
                    attrs['end'] = start
                else:
                    attrs['end'] = start + timedelta(hours=1)
        return attrs

    def create(self, validated_data):
        if 'created_by' not in validated_data:
            request = self.context.get('request') if isinstance(self.context, dict) else None
            user = getattr(request, 'user', None)
            if user and getattr(user, 'is_authenticated', False):
                validated_data['created_by'] = user
        return super().create(validated_data)

    def get_assignees_display(self, obj):
        try:
            names = []
            for u in obj.assignees.all():
                first = (getattr(u, 'first_name', '') or '').strip()
                last = (getattr(u, 'last_name', '') or '').strip()
                full = f"{first} {last}".strip()
                if full:
                    names.append(full)
                    continue
                username = (getattr(u, 'username', '') or '').strip()
                # Если username не похож на email — используем его; иначе email
                if username and '@' not in username:
                    names.append(username)
                else:
                    email = (getattr(u, 'email', '') or '').strip()
                    names.append(email or username)
            return names
        except Exception:
            return []

class TaskListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    client_id = serializers.SerializerMethodField()
    assignees = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'task_type', 'start', 'end', 'all_day', 'status', 'client_name', 'client_id', 'assignees']

    def get_client_name(self, obj):
        c = getattr(obj, 'client', None)
        if not c:
            return None
        return f"{c.first_name or ''} {c.last_name or ''}".strip() or None

    def get_client_id(self, obj):
        c = getattr(obj, 'client', None)
        return c.id if c else None

    def get_assignees(self, obj):
        try:
            return list(obj.assignees.values_list('id', flat=True))
        except Exception:
            # Fallback if relation not available
            return []

# --- Уведомления ---
class NotificationSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    reminder_type = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'source', 'is_read', 'created_at', 'client', 'client_name', 'reminder', 'reminder_type', 'user_name']

    def get_client_name(self, obj):
        try:
            c = obj.client
            if not c:
                return ''
            return f"{c.first_name} {c.last_name}".strip()
        except Exception:
            return ''

    def get_reminder_type(self, obj):
        try:
            return obj.reminder.get_reminder_type_display() if obj.reminder else ''
        except Exception:
            return ''

    def get_user_name(self, obj):
        """Отображаем именно ответственного менеджера клиента (client.created_by),
        а не владельца записи уведомления, чтобы не путать при fallback.
        Если менеджер отсутствует — возвращаем пустую строку.
        """
        try:
            client = obj.client
            if not client or not getattr(client, 'created_by', None):
                return ''
            u = client.created_by
            full = f"{u.first_name or ''} {u.last_name or ''}".strip()
            return full or u.username or u.email
        except Exception:
            return ''