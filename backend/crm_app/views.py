import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.shortcuts import redirect
from .models import User, EmailVerificationToken
from django.db import models
from .serializers import UserRegistrationSerializer, EmailAuthTokenSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
import random # Если его еще нет
from django.core.mail import send_mail # Если его еще нет
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Client, LegalCase, Document, Task, Reminder, Company, Invite, Notification
from .billing.plans import get_plan_limits, format_usage
from django.db.models import Sum
from .serializers import ClientListSerializer, ClientSerializer, LegalCaseSerializer, TaskSerializer, TaskListSerializer, \
    ProfileSerializer, ChangePasswordSerializer, CompanySerializer, UserAdminSerializer, InviteSerializer, NotificationSerializer
from urllib.parse import urlparse
from django.db.utils import OperationalError

def _create_notification(user, title, message='', client=None, reminder=None, source='SYSTEM'):
    """
    Create a notification:
    - If a concrete authenticated user is provided -> only for that user.
    - If user is None OR not authenticated (e.g. public registration/password reset flows) ->
      broadcast to internal staff (ADMIN / LEAD / LAWYER) so they can see email activity.
    This allows notifications to appear even when the action was triggered anonymously.
    """
    try:
        recipients = []
        if user and getattr(user, 'is_authenticated', False):
            recipients = [user]
        else:
            # Broadcast to all internal (не клиентские) роли
            recipients = list(User.objects.filter(role__in=['ADMIN', 'LEAD', 'LAWYER', 'MANAGER', 'ASSISTANT']))
        title_safe = (title or '')[:200]
        msg = message or ''
        for r in recipients:
            try:
                Notification.objects.create(
                    user=r,
                    title=title_safe,
                    message=msg,
                    client=client,
                    reminder=reminder,
                    source=source
                )
            except Exception:
                continue
    except Exception:
        pass

def _safe_send_mail(subject: str, body: str, to: list[str], html_body: str | None = None) -> bool:
    """Send mail with robust exception handling and optional HTML.
    Returns True if SMTP reports success, False otherwise.
    Prints diagnostic info when DEBUG is enabled.
    """
    from django.conf import settings
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if html_body:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(subject, body, from_email, to)
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            return True
        sent = send_mail(subject, body, from_email, to, fail_silently=False)
        return bool(sent)
    except Exception as e:
        try:
            if getattr(settings, 'DEBUG', False):
                print('[email][error]', subject, '->', to, 'exception:', repr(e))
        except Exception:
            pass
        try:
            # Last attempt silent
            send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), to, fail_silently=True)
        except Exception:
            pass
        return False


def _safe_send_mail(subject: str, body: str, to: list[str], html_body: str | None = None) -> bool:
    """Send mail with robust exception handling and optional HTML.
    Returns True if SMTP reports success, False otherwise.
    Prints diagnostic info when DEBUG is enabled.
    """
    from django.conf import settings
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if html_body:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(subject, body, from_email, to)
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            return True
        sent = send_mail(subject, body, from_email, to, fail_silently=False)
        return bool(sent)
    except Exception as e:
        try:
            if getattr(settings, 'DEBUG', False):
                print('[email][error]', subject, '->', to, 'exception:', repr(e))
        except Exception:
            pass
        try:
            # Last attempt silent
            send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), to, fail_silently=True)
        except Exception:
            pass
        return False


def _get_frontend_base(request):
    """Detect frontend base URL from request headers (Origin/Referer) with env fallback.
    Returns a string like 'http://localhost:8080' without trailing slash.
    """
    base = None
    try:
        origin = request.META.get('HTTP_ORIGIN') or request.META.get('HTTP_REFERER')
        if origin:
            p = urlparse(origin)
            if p.scheme and p.netloc:
                base = f"{p.scheme}://{p.netloc}"
    except Exception:
        base = None
    if not base:
        try:
            base = getattr(settings, 'FRONTEND_URL', 'http://localhost:8080')
        except Exception:
            base = 'http://localhost:8080'
    return (base or 'http://localhost:8080').rstrip('/')


def send_welcome_verification_email(user: User, token: str):
    """Send a branded welcome + email verification code to the user (HTML + text)."""
    try:
        first_name = (getattr(user, 'first_name', '') or '').strip()
        display_name = first_name or (getattr(user, 'username', '') or '').strip() or 'друг'
        frontend = getattr(settings, 'FRONTEND_URL', 'http://localhost:8080')
        # Include token so the page can auto-verify on open
        verify_url = f"{frontend}/verify-email?email={user.email}&token={token}"
        subject = 'Добро пожаловать в CRM LegalFlow — подтвердите email'
        context = {
            'display_name': display_name,
            'email': user.email,
            'token': token,
            'verify_url': verify_url,
            'product': 'CRM LegalFlow',
            'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@legalflow.pl'),
        }
        text_body = None
        html_body = None
        try:
            text_body = render_to_string('email/welcome_verification.txt', context)
        except Exception:
            text_body = (
                f"Здравствуйте, {display_name}!\n\n"
                f"Спасибо за регистрацию в CRM LegalFlow. Для завершения процедуры введите код подтверждения:\n\n"
                f"Код: {token}\n\n"
                f"Вы также можете перейти по ссылке и ввести код на странице подтверждения:\n{verify_url}\n\n"
                f"Если вы не запрашивали регистрацию, просто проигнорируйте это письмо.\n\n"
                f"С уважением, команда CRM LegalFlow\n"
            )
        try:
            html_body = render_to_string('email/welcome_verification.html', context)
        except Exception:
            html_body = None

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@legalflow.pl')
        msg = EmailMultiAlternatives(subject, text_body, from_email, [user.email])
        if html_body:
            msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
    except Exception:
        # Fallback to a very simple mail in case templates or EmailMultiAlternatives fail
        try:
            subject = 'Подтверждение регистрации'
            send_mail(subject, f'Код подтверждения: {token}', getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@legalflow.pl'), [user.email], fail_silently=False)
        except Exception:
            pass


class RegisterRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        company_name = data.get('company_name') or data.get('company') or data.get('org')
        # Username не запрашиваем на форме: по умолчанию используем email
        username = (data.get('username') or email or '').strip().lower()

        if not email or not password:
            return Response({'error': 'Email и пароль обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        # Helper: ensure company + trial for a user without company
        def _ensure_trial_company(u: User):
            try:
                if getattr(u, 'company_id', None):
                    return u.company
                # создаём компанию
                # Приоритет: переданное имя компании -> username -> email -> дефолт
                name_seed = (company_name or u.username or u.email or 'Моя компания').strip()
                if not name_seed:
                    name_seed = 'Моя компания'
                company = Company.objects.create(name=name_seed[:200], owner=u, plan='TRIAL')
                # Инициализация trial если не установлено
                if not company.trial_started_at:
                    company.trial_started_at = timezone.now()
                    from datetime import timedelta
                    company.trial_ends_at = company.trial_started_at + timedelta(days=14)
                    company.save(update_fields=['trial_started_at', 'trial_ends_at'])
                # Привязка пользователя
                u.company = company
                u.save(update_fields=['company'])
                # Генерация invite_code если пусто
                if not company.invite_code:
                    import secrets
                    company.invite_code = secrets.token_urlsafe(24)
                    company.save(update_fields=['invite_code'])
                return company
            except Exception:
                return None

        # Если пользователь с таким email уже существует
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_active:
                return Response({
                    'error': 'Пользователь с таким email уже зарегистрирован. Войдите в систему или воспользуйтесь восстановлением пароля.',
                    'error_code': 'USER_EXISTS'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Пользователь не подтвержден: обновим пароль (username оставляем как есть)
            user.set_password(password)
            # Убедимся, что статус до подтверждения корректный
            user.is_active = False
            user.is_client = False
            user.is_manager = True
            user.save()
            # Сбросим старый токен и создадим новый
            EmailVerificationToken.objects.filter(user=user).delete()
            token = ''.join(random.choices('0123456789', k=6))
            EmailVerificationToken.objects.create(user=user, token=token)
            # Отправляем приветственное письмо с кодом (не создаём уведомление и не раскрываем код в API)
            send_welcome_verification_email(user, token)
            # Не создаём уведомление о письме подтверждения
            company = _ensure_trial_company(user)
            trial_block = None
            if company:
                trial_block = {
                    'plan': company.plan,
                    'trial_started_at': company.trial_started_at,
                    'trial_ends_at': company.trial_ends_at,
                    'company_name': company.name,
                }
            return Response({
                'message': 'Письмо для подтверждения отправлено на ваш email.',
                'info': 'Ранее начата регистрация. Аккаунт активируется после ввода кода из письма.',
                'status_code': 'VERIFICATION_RESENT',
                'trial': trial_block
            }, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            # Регистрируем нового пользователя стандартным путем (username = email)
            serializer = UserRegistrationSerializer(data={'username': username, 'email': email, 'password': password})
            if serializer.is_valid():
                user = serializer.save(is_client=True)
                token = ''.join(random.choices('0123456789', k=6))
                EmailVerificationToken.objects.create(user=user, token=token)
                # Отправляем приветственное письмо с кодом
                send_welcome_verification_email(user, token)
                # Не создаём уведомление о коде подтверждения и не включаем код в ответ
                # Автосоздание компании + trial
                company = _ensure_trial_company(user)
                trial_block = None
                if company:
                    trial_block = {
                        'plan': company.plan,
                        'trial_started_at': company.trial_started_at,
                        'trial_ends_at': company.trial_ends_at,
                        'company_name': company.name,
                    }
                return Response({'message': 'Письмо для подтверждения отправлено на ваш email.', 'trial': trial_block}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        token = request.data.get('token')

        if not email or not token:
            return Response({'error': 'Email и токен обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
            verification_token = EmailVerificationToken.objects.get(user=user, token=token)

            # ПРОВЕРКА: если прошло больше 5 минут, код недействителен
            if timezone.now() > verification_token.created_at + timedelta(minutes=5):
                verification_token.delete()
                return Response({'error': 'Срок действия кода истёк.'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            # Если в системе еще нет менеджеров, первый подтвержденный пользователь становится менеджером
            try:
                if not User.objects.filter(is_manager=True).exists():
                    user.is_manager = True
                    user.is_client = False
                    user.save()
            except Exception:
                pass
            verification_token.delete()
            return Response({'message': 'Регистрация успешно завершена!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Неверный токен.'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            # If credentials invalid, this raises serializers.ValidationError -> return 400 with details
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            try:
                token, created = Token.objects.get_or_create(user=user)
            except OperationalError as oe:
                # Likely missing migrations for rest_framework.authtoken
                return Response(
                    {
                        'detail': 'migrations_missing',
                        'hint': 'Apply migrations for auth token app (python manage.py migrate).'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            # Update last_login for token-based auth so admin can see recent activity
            try:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            except Exception:
                pass
            return Response({'token': token.key, 'user_id': user.pk, 'email': user.email})
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            if isinstance(e, ValidationError):
                # Propagate validation details (e.detail typically contains non_field_errors)
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            # Unexpected error: don't crash with 500 in frontend; return generic error (and log server-side)
            try:
                import logging
                logging.getLogger(__name__).exception('LoginView unexpected error')
            except Exception:
                pass
            return Response({'detail': 'internal_error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return Response({'error': 'Email обязателен.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            subject = 'Сброс пароля для вашей CRM-системы'
            # Генерируем ссылку на фронтенд: берём Origin/Referer, иначе FRONTEND_URL
            frontend_base = _get_frontend_base(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"{frontend_base}/password-reset/confirm/{uid}/{token}/"
            display_name = getattr(user, 'first_name', '') or getattr(user, 'username', '') or user.email
            message = (
                f"Здравствуйте, {display_name}.\n\n"
                f"Для сброса пароля перейдите по ссылке: {reset_link}\n\n"
                f"Если вы не запрашивали сброс пароля, проигнорируйте это письмо.\n\n"
                f"С уважением,\nCRM LegalFlow\n\n"
                f"------------------------------------------------------------\n\n"
                f"Dzień dobry, {display_name},\n\n"
                f"Aby zresetować hasło, przejdź pod link: {reset_link}\n\n"
                f"Jeśli nie prosiłeś(-aś) o reset hasła, zignoruj tę wiadomość.\n\n"
                f"Pozdrawiamy,\nCRM LegalFlow"
            )

            # Пытаемся отправить письмо; при сбое не падаем 500, а возвращаем 200 с подсказкой
            mail_ok = _safe_send_mail(subject, message, [user.email])

            # Больше не создаём системное уведомление о сбросе пароля

            return Response({
                'message': 'Если email существует, ссылка для сброса пароля отправлена.',
                'email_delivery': 'ok' if mail_ok else 'failed'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Произошла ошибка при обработке запроса.'}, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('password')

        if not all([uidb64, token, new_password]):
            return Response({'error': 'Все поля обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, {'new_password1': new_password, 'new_password2': new_password})
            if form.is_valid():
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Пароль успешно сброшен!'}, status=status.HTTP_200_OK)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Неверная ссылка или токен.'}, status=status.HTTP_400_BAD_REQUEST)
        
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated] # <-- Проверяем аутентификацию

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': bool(getattr(user, 'is_superuser', False)),
            'is_client': getattr(user, 'is_client', False),
            'is_manager': getattr(user, 'is_manager', False),
            'role': getattr(user, 'role', 'ADMIN'),
            'company_id': getattr(user.company, 'id', None)
        })

from django.db.models import Count
from django.db.models import Case, When, Value, IntegerField, F, DateTimeField

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not getattr(user, 'is_superuser', False):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        # Companies and plans
        companies = Company.objects.all().values('id', 'name', 'plan', 'created_at', 'trial_started_at', 'trial_ends_at', 'owner_id')
        plans = Company.objects.values('plan').annotate(count=Count('id')).order_by('plan')

        # Users and roles
        users_total = User.objects.count()
        users_by_role = User.objects.values('role').annotate(count=Count('id')).order_by('role')
        # For the admin dashboard: provide a compact list of users with last login info
        # Use annotate to alias related fields before extracting with values
        users_list = list(
            User.objects.select_related('company')
            .annotate(company_name=F('company__name'))
            .values(
                'id', 'username', 'email', 'first_name', 'last_name', 'role',
                'last_login', 'company_name', 'company_id'
            )
            .order_by(F('last_login').desc(nulls_last=True), 'id')
        )

        # Per-company user counts
        company_user_counts = User.objects.values('company_id').annotate(count=Count('id'))
        counts_map = {row['company_id']: row['count'] for row in company_user_counts}

        # Other entities
        clients_total = Client.objects.count()
        cases_total = LegalCase.objects.count()
        tasks_total = Task.objects.count()
        reminders_total = Reminder.objects.count()

        companies_detail = []
        for c in companies:
            companies_detail.append({
                'id': c['id'],
                'name': c['name'],
                'plan': c['plan'],
                'created_at': c['created_at'],
                'trial_started_at': c['trial_started_at'],
                'trial_ends_at': c['trial_ends_at'],
                'users_count': counts_map.get(c['id'], 0),
            })

        payload = {
            'totals': {
                'companies': len(companies_detail),
                'users': users_total,
                'clients': clients_total,
                'cases': cases_total,
                'tasks': tasks_total,
                'reminders': reminders_total,
            },
            'plans': list(plans),
            'usersByRole': list(users_by_role),
            'users': users_list,
            'companies': companies_detail,
        }
        return Response(payload)

# --- Профиль пользователя ---
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def put(self, request):
        ser = ProfileSerializer(request.user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        old = ser.validated_data['old_password']
        new = ser.validated_data['new_password']
        if not request.user.check_password(old):
            return Response({'detail': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new)
        request.user.save()
        return Response({'detail': 'Пароль обновлен'})

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        if not password:
            return Response({'detail': 'Пароль обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(password):
            return Response({'detail': 'Неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)

        # Если пользователь владелец компании — отвязываем, чтобы не удалить компанию каскадом
        try:
            company = getattr(request.user, 'owned_company', None)
            if company:
                company.owner = None
                company.save(update_fields=['owner'])
        except Exception:
            pass

        # Удаляем пользователя
        request.user.delete()
        return Response({'detail': 'Аккаунт удален'}, status=status.HTTP_200_OK)

# --- Настройки компании (админ) ---
class CompanySettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response({'detail': 'Компания не привязана'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanySerializer(company).data)

    def put(self, request):
        if request.user.role not in ('ADMIN', 'LEAD', 'LAWYER'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        company = request.user.company
        if not company:
            # Создаем компанию, если её нет (первый администратор)
            company = Company.objects.create(name=request.data.get('name') or 'Моя компания', owner=request.user)
            # Инициализация trial если отсутствует
            try:
                if not company.trial_started_at:
                    company.trial_started_at = timezone.now()
                    from datetime import timedelta
                    company.trial_ends_at = company.trial_started_at + timedelta(days=14)
                    company.plan = 'TRIAL'
                    company.save(update_fields=['trial_started_at', 'trial_ends_at', 'plan'])
            except Exception:
                pass
            request.user.company = company
            request.user.save()
        # Разрешаем изменять настройки только создателю (владельцу) компании
        try:
            owner_id = getattr(company, 'owner_id', None)
            if owner_id and owner_id != request.user.id:
                return Response({'detail': 'Только создатель компании может изменять её настройки.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            # В случае неожиданной ошибки идентификации владельца — запретим изменение
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        ser = CompanySerializer(company, data=request.data, partial=True)
        if ser.is_valid():
            obj = ser.save()
            if not obj.invite_code:
                import secrets
                obj.invite_code = secrets.token_urlsafe(24)
                obj.save(update_fields=['invite_code'])
            return Response(CompanySerializer(obj).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class UsersAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        qs = request.user.company.users.all() if request.user.company else User.objects.none()
        return Response(UserAdminSerializer(qs, many=True).data)

    def post(self, request):
        # Создавать пользователей вручную могут только администратор и руководитель
        if request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        password = data.pop('password', None)
        ser = UserAdminSerializer(data=data)
        if ser.is_valid():
            user = User.objects.create(**ser.validated_data)
            if password:
                user.set_password(password)
            user.company = request.user.company
            user.save()
            return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = request.user.company.users.get(pk=pk)
        except Exception:
            return Response({'detail': 'Не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Нельзя менять роль владельца компании на что-либо кроме ADMIN
        incoming_role = request.data.get('role')
        if incoming_role and incoming_role != 'ADMIN':
            company = request.user.company
            if company and getattr(company, 'owner_id', None) == user.id:
                return Response({'detail': 'Создатель CRM всегда администратор'}, status=status.HTTP_400_BAD_REQUEST)
        ser = UserAdminSerializer(user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        try:
            user = request.user.company.users.get(pk=pk)
        except Exception:
            return Response({'detail': 'Не найден'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- Приглашения ---
class InviteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        if not request.user.company:
            return Response({'detail': 'Сначала создайте компанию'}, status=status.HTTP_400_BAD_REQUEST)
        import secrets
        token = secrets.token_urlsafe(32)
        invite = Invite.objects.create(
            token=token,
            company=request.user.company,
            role=request.data.get('role') or 'MANAGER',
            created_by=request.user
        )
        return Response(InviteSerializer(invite).data, status=status.HTTP_201_CREATED)

class InviteAcceptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password')
        desired_username = request.data.get('username')
        first_name = (request.data.get('first_name') or '').strip()
        last_name = (request.data.get('last_name') or '').strip()
        if not all([token, email, password]):
            return Response({'detail': 'token, email, password обязательны'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            invite = Invite.objects.get(token=token, is_active=True)
        except Invite.DoesNotExist:
            return Response({'detail': 'Приглашение не найдено'}, status=status.HTTP_404_NOT_FOUND)
        # Создаём пользователя и привязываем к компании
        if User.objects.filter(email__iexact=email).exists():
            return Response({'detail': 'Email уже используется'}, status=status.HTTP_400_BAD_REQUEST)
        # Выберем имя пользователя: из формы, если свободно; иначе fallback к email
        username_value = ((desired_username or '').strip() or email).lower()
        try:
            if username_value and User.objects.filter(username__iexact=username_value).exists():
                # если занято — используем email как имя пользователя
                username_value = email
        except Exception:
            username_value = email
        # Приглашение теперь тоже требует подтверждения email: создаем НЕактивного пользователя и отправляем код
        user = User.objects.create_user(username=username_value, email=email, password=password, is_active=False, role=invite.role)
        if first_name:
            user.first_name = first_name[:150]
        if last_name:
            user.last_name = last_name[:150]
        user.company = invite.company
        user.is_manager = True  # для обратной совместимости меню
        user.save()
        # Сгенерировать и отправить код подтверждения
        try:
            EmailVerificationToken.objects.filter(user=user).delete()
        except Exception:
            pass
        code = ''.join(random.choices('0123456789', k=6))
        EmailVerificationToken.objects.create(user=user, token=code)
        # Отправляем приветственное письмо с кодом подтверждения (устойчиво к ошибкам SMTP)
        send_welcome_verification_email(user, code)
        # Не создаём уведомление о коде подтверждения для приглашения
        # Деактивируем приглашение, чтобы его нельзя было использовать повторно
        invite.is_active = False
        invite.save(update_fields=['is_active'])
        return Response({'detail': 'Письмо для подтверждения отправлено на ваш email.', 'requires_verification': True, 'email': user.email}, status=status.HTTP_201_CREATED)
    
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        try:
            user = User.objects.get(email__iexact=email, is_active=False)
            # Удаляем старый токен, если он был
            EmailVerificationToken.objects.filter(user=user).delete()

            # Создаем и отправляем новый
            token = ''.join(random.choices('0123456789', k=6))
            EmailVerificationToken.objects.create(user=user, token=token)

            # Используем единый шаблон приветствия + код, чтобы не падать при сбоях SMTP
            send_welcome_verification_email(user, token)
            return Response({'message': 'Письмо для подтверждения отправлено.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден или уже активен.'}, status=status.HTTP_404_NOT_FOUND)


class BillingUsageView(APIView):
    """Возвращает текущий план и использование по лимитам.
    Первичная реализация (без кеширования, оптимизировать позже при росте данных).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        if not company:
            return Response({'detail': 'Компания не привязана'}, status=status.HTTP_400_BAD_REQUEST)
        plan_code = company.plan or 'STARTER'
        trial_started = company.trial_started_at
        trial_ends = company.trial_ends_at
        now_ts = timezone.now()
        trial_days_left = None
        trial_expired = False
        if trial_ends:
            delta = trial_ends - now_ts
            trial_days_left = max(delta.days, 0)
            trial_expired = now_ts > trial_ends
        limits = get_plan_limits(plan_code)

        # Подсчёт usage
        # users: включая все связанные с company пользователи
        users_count = company.users.count()
        # clients: созданные сотрудниками компании или привязанные через user.company
        clients_count = Client.objects.filter(
            models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
        ).count()
        cases_count = 0
        try:
            cases_count = LegalCase.objects.filter(client__in=Client.objects.filter(
                models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
            )).count()
        except Exception:
            pass
        files_qs = Document.objects.filter(legal_case__client__in=Client.objects.filter(
            models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
        ))
        # Количество файлов
        files_count = 0
        try:
            from .models import UploadedFile
            files_count = UploadedFile.objects.filter(document__in=files_qs).count()
            # Суммарный вес хранить позже (сейчас не всегда FileField size доступен быстро)
            total_storage_mb = 0
            try:
                total_size = UploadedFile.objects.filter(document__in=files_qs).aggregate(s=Sum('file'))
            except Exception:
                total_storage_mb = 0
        except Exception:
            total_storage_mb = 0

        # Tasks за текущий месяц
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        tasks_month = Task.objects.filter(
            client__in=Client.objects.filter(
                models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
            ),
            created_at__gte=month_start
        ).count() if hasattr(Task, 'created_at') else 0

        # Active reminders (sent_at is null)
        reminders_active = Reminder.objects.filter(
            client__in=Client.objects.filter(
                models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
            ),
            sent_at__isnull=True
        ).count()

        # Emails per month (пока нет лога — 0)
        emails_month = 0

        raw_usage = {
            'users': users_count,
            'clients': clients_count,
            'cases': cases_count,
            'files': files_count,
            'files_storage_mb': 0,  # пока не считаем вес
            'tasks_per_month': tasks_month,
            'reminders_active': reminders_active,
            'emails_per_month': emails_month,
        }
        formatted = format_usage(limits, raw_usage)
        return Response({
            'plan': plan_code,
            'limits': limits,
            'usage': formatted,
            'trial': {
                'started_at': trial_started,
                'ends_at': trial_ends,
                'days_left': trial_days_left,
                'expired': trial_expired,
            },
            'read_only': trial_expired and plan_code == 'TRIAL'
        })

class BillingUpgradeView(APIView):
    """Endpoint апгрейда плана (временный, без оплаты).
    Поддерживаемые сценарии:
      - TRIAL -> STARTER | PRO
      - STARTER -> PRO
    В запросе можно передать {"target_plan": "PRO"} или "STARTER"; по умолчанию STARTER.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target = str(request.data.get('target_plan') or 'STARTER').upper()
        if target not in ('STARTER', 'PRO'):
            return Response({'detail': 'Недопустимый target_plan'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        company = getattr(user, 'company', None)
        if not company:
            return Response({'detail': 'Компания не найдена'}, status=status.HTTP_400_BAD_REQUEST)
        current = company.plan.upper() if company.plan else 'TRIAL'
        if current == target:
            return Response({'detail': f'Уже на плане {target}'}, status=status.HTTP_200_OK)
        allowed = False
        if current == 'TRIAL' and target in ('STARTER', 'PRO'):
            allowed = True
        elif current == 'STARTER' and target == 'PRO':
            allowed = True
        if not allowed:
            return Response({'detail': f'Нельзя перейти с {current} на {target}'}, status=status.HTTP_400_BAD_REQUEST)
        company.plan = target
        company.save(update_fields=['plan'])
        return Response({'message': f'Plan upgraded to {target}', 'plan': company.plan}, status=status.HTTP_200_OK)
        
class ClientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Скоуп по компании и роли
        if request.user.role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and request.user.company_id:
            # Руководители: клиенты в пределах своей компании.
            # Включаем: (a) созданные сотрудниками компании, (b) где client.user привязан к этой компании.
            company_id = request.user.company_id
            clients = Client.objects.filter(
                models.Q(created_by__company_id=company_id) |
                models.Q(user__company_id=company_id)
            )
        else:
            # Прочие: только своих клиентов
            clients = Client.objects.filter(created_by=request.user)

        # Фильтр по периоду (дата создания) — уважаем локальный часовой пояс (settings.TIME_ZONE)
        # Проблема с created_at__date: извлечение даты происходит в UTC, что сдвигает сутки.
        # Поэтому считаем границы дня в локальной зоне и фильтруем по created_at__gte / __lt.
        created_from = request.query_params.get('created_from')  # YYYY-MM-DD
        created_to = request.query_params.get('created_to')      # YYYY-MM-DD
        if created_from or created_to:
            try:
                from datetime import datetime, date, time, timedelta
                tz = timezone.get_current_timezone()
                start_dt = None
                end_dt = None
                if created_from:
                    d_from = date.fromisoformat(created_from)
                    start_dt = timezone.make_aware(datetime.combine(d_from, time.min), tz)
                if created_to:
                    d_to = date.fromisoformat(created_to)
                    # конец периода — начало следующего дня (исключительно)
                    end_dt = timezone.make_aware(datetime.combine(d_to + timedelta(days=1), time.min), tz)
                if start_dt:
                    clients = clients.filter(created_at__gte=start_dt)
                if end_dt:
                    clients = clients.filter(created_at__lt=end_dt)
            except Exception:
                # Молча пропускаем при неверном формате дат
                pass

        # Фильтр по менеджеру/создателю (created_by: id | 'me')
        created_by_param = request.query_params.get('created_by')
        if created_by_param:
            try:
                clients = clients.filter(created_by_id=int(created_by_param))
            except Exception:
                pass

        # Сортировка по дате добавления
        sort = request.query_params.get('sort')  # 'created_at' | '-created_at'
        if sort in ('created_at', '-created_at'):
            clients = clients.order_by(sort)
        else:
            clients = clients.order_by('-created_at')
        try:
            serializer = ClientListSerializer(clients, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Вернем текст ошибки для быстрой диагностики на фронте
            return Response({'detail': 'internal_error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ДОБАВЛЯЕМ МЕТОД POST
    def post(self, request):
        # Все аутентифицированные пользователи могут создавать клиентов.
        # Ответственный менеджер (created_by):
        #  - ADMIN/LEAD могут указать ответственного менеджера явным образом через responsible_manager_id
        #  - MANAGER не может назначать другого — назначается сам автоматически
        #  - ASSISTANT не может создавать клиентов
        if getattr(request.user, 'role', None) == 'ASSISTANT':
            return Response({'detail': 'Ассистент не может создавать клиентов'}, status=status.HTTP_403_FORBIDDEN)
        # Уберем служебные поля из запроса, чтобы сериализатор не ругался на неизвестные
        data = request.data.copy()
        raw_manager_id = data.pop('responsible_manager_id', None) or data.pop('created_by_id', None)
        serializer = ClientSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        creator = request.user
        role = getattr(creator, 'role', None)
        responsible_manager = creator

        # Попытка указать ответственного менеджера через тело запроса
    # Уже извлекли выше из копии data

        if role in ('ADMIN', 'LEAD'):
            # Разрешаем назначение только сотрудников своей компании с ролью MANAGER или LEAD
            if raw_manager_id:
                try:
                    candidate = User.objects.get(pk=int(raw_manager_id))
                    if (getattr(candidate, 'company_id', None) and getattr(creator, 'company_id', None)
                        and candidate.company_id == creator.company_id
                        and getattr(candidate, 'role', None) in ('MANAGER', 'LEAD')):
                        responsible_manager = candidate
                    else:
                        return Response({'detail': 'Можно назначать только менеджера/руководителя своей компании.'}, status=status.HTTP_400_BAD_REQUEST)
                except (User.DoesNotExist, ValueError, TypeError):
                    return Response({'detail': 'Указан некорректный менеджер.'}, status=status.HTTP_400_BAD_REQUEST)
            # Если не указан — по умолчанию назначим создателя (админа/руководителя)
        else:
            # Любые попытки манипулировать ответственным менеджером игнорируем для не-ADMIN/LEAD
            responsible_manager = creator

        client = serializer.save(created_by=responsible_manager)
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
    
class ClientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Доступ:
        # - ADMIN/LEAD: любой клиент в пределах своей компании (по created_by.company или client.user.company)
        # - Прочие: только свои клиенты (created_by == request.user)
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(client, 'created_by', None), 'company_id', None)
            client_user_company_id = getattr(getattr(client, 'user', None), 'company_id', None)
            if user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id):
                pass
            else:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if client.created_by_id and client.created_by_id != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        role = getattr(request.user, 'role', None)
        if role == 'ASSISTANT':
            return Response({'detail': 'Ассистент не может редактировать клиента'}, status=status.HTTP_403_FORBIDDEN)
        if role in ('ADMIN', 'LEAD', 'LAWYER'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(client, 'created_by', None), 'company_id', None)
            client_user_company_id = getattr(getattr(client, 'user', None), 'company_id', None)
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Разрешаем изменять только клиентов, созданных этим аккаунтом
            if client.created_by_id and client.created_by_id != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = ClientSerializer(client, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Удаление клиента.
        Правила доступа:
        - ADMIN / LEAD / LAWYER могут удалять клиента своей компании (по created_by.company или client.user.company)
        - MANAGER может удалить только своих клиентов (created_by == self)
        - ASSISTANT не может удалять
        При удалении чистим связанные объекты каскадно вручную (дела, документы, задачи, напоминания),
        чтобы избежать накопления "осиротевших" записей, затем удаляем сам клиент и связанного user (если он не использован где-то ещё).
        """
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'detail': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)

        role = getattr(request.user, 'role', None)
        if role == 'ASSISTANT':
            return Response({'detail': 'Ассистент не может удалять клиентов'}, status=status.HTTP_403_FORBIDDEN)

        # Проверяем доступ
        if role in ('ADMIN', 'LEAD', 'LAWYER'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(client, 'created_by', None), 'company_id', None)
            client_user_company_id = getattr(getattr(client, 'user', None), 'company_id', None)
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:  # MANAGER
            if client.created_by_id and client.created_by_id != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        # Выполняем удаление с защитой от неожиданных исключений
        from django.db import transaction
        try:
            with transaction.atomic():
                # Удаляем связанные задачи
                client.tasks.all().delete()
                # Удаляем связанные напоминания (их уведомления тоже будут удалены через on_delete=SET_NULL, но подчистим отдельно)
                client.reminders.all().delete()
                # Удаляем связанные дела (документы и файлы пойдут каскадом)
                client.legal_cases.all().delete()
                # Удаляем уведомления напрямую
                client.notifications.all().delete()
                # Сохраняем ссылку на связанного user, чтобы удалить его после удаления клиента если он не используется
                related_user = client.user
                client.delete()
                # Если у пользователя нет больше client_profile и он не активирован как отдельный сотрудник/менеджер — можно удалить
                if related_user and not hasattr(related_user, 'client_profile'):
                    # Он мог быть общим сотрудником — не трогаем активных/менеджеров
                    if getattr(related_user, 'is_client', False) and not getattr(related_user, 'is_active', False):
                        # Дополнительно убеждаемся, что он не создатель других клиентов
                        if not related_user.created_clients.exists():
                            related_user.delete()
        except Exception as e:
            return Response({'detail': 'Ошибка при удалении', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CaseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_pk):
        try:
            client = Client.objects.get(pk=client_pk)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Доступ к созданию дела:
        # - ADMIN/LEAD/LAWYER: для клиентов своей компании
        # - MANAGER: только для своих клиентов
        # - ASSISTANT: запрещено
        role = getattr(request.user, 'role', None)
        if role == 'ASSISTANT':
            return Response({'detail': 'Ассистент не может создавать дела'}, status=status.HTTP_403_FORBIDDEN)
        if role in ('ADMIN', 'LEAD', 'LAWYER'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(client, 'created_by', None), 'company_id', None)
            client_user_company_id = getattr(getattr(client, 'user', None), 'company_id', None)
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if client.created_by_id and client.created_by_id != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = LegalCaseSerializer(data=request.data)
        if serializer.is_valid():
            # При сохранении передаем клиента, чтобы связать с ним дело
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- КАЛЕНДАРЬ / ЗАДАЧИ ---
class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Видимость задач:
        # - ADMIN/LEAD/LAWYER/ASSISTANT: задачи по клиентам своей компании
        # - MANAGER: задачи только по своим клиентам
        base_qs = Task.objects.select_related('client', 'created_by')
        if request.user.role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and request.user.company_id:
            # Видимость: задачи по клиентам своей компании или личные задачи сотрудников компании
            qs = base_qs.filter(
                models.Q(client__created_by__company_id=request.user.company_id) |
                models.Q(client__user__company_id=request.user.company_id) |
                models.Q(client__isnull=True, created_by__company_id=request.user.company_id)
            )
        else:
            # Менеджер: свои задачи + те, где он в исполнителях
            qs = base_qs.filter(
                models.Q(client__created_by=request.user) |
                models.Q(client__isnull=True, created_by=request.user) |
                models.Q(assignees=request.user)
            )
        # Фильтры
        task_types = request.query_params.get('types')  # CSV
        status_filter = request.query_params.get('status')
        client_q = request.query_params.get('client')
        search = request.query_params.get('q')
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        if task_types:
            type_values = [t.strip() for t in task_types.split(',') if t.strip()]
            if type_values:
                qs = qs.filter(task_type__in=type_values)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if client_q:
            qs = qs.filter(client_id=client_q)
        if search:
            qs = qs.filter(models.Q(title__icontains=search) | models.Q(description__icontains=search))
        if start and end:
            qs = qs.filter(end__gte=start, start__lte=end)

        # Сортировка: ближайшие задачи сверху, прошедшие — внизу
        now = timezone.now()
        try:
            qs = qs.annotate(
                is_past=Case(
                    When(start__lt=now, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                ),
                sort_start=Case(
                    When(start__lt=now, then=Value(None, output_field=DateTimeField())),
                    default=F('start'),
                    output_field=DateTimeField()
                ),
            ).order_by('is_past', 'sort_start', '-start')
        except Exception:
            # если БД не поддерживает такую сортировку — fallback по start
            qs = qs.order_by('start')
        serializer = TaskSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            client = serializer.validated_data.get('client')
            if client:  # Проверяем права только если клиент указан
                role = getattr(request.user, 'role', None)
                if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
                    user_company_id = getattr(request.user, 'company_id', None)
                    owner_company_id = getattr(getattr(client, 'created_by', None), 'company_id', None)
                    client_user_company_id = getattr(getattr(client, 'user', None), 'company_id', None)
                    if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                        return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    if client.created_by_id and client.created_by_id != request.user.id:
                        return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
            # Сохраняем задачу с создателем
            task = serializer.save(created_by=request.user)
            # Если в запросе переданы назначенные исполнители — добавим их
            try:
                assignee_ids = request.data.get('assignees') or []
                if isinstance(assignee_ids, list) and assignee_ids:
                    users = User.objects.filter(id__in=[int(i) for i in assignee_ids if str(i).isdigit()])
                    if users:
                        task.assignees.add(*list(users))
            except Exception:
                pass
            # Создаём уведомления только для назначенных МЕНЕДЖЕРОВ (кроме автора)
            try:
                # Подготовим имя постановщика задачи (создателя)
                creator = request.user
                creator_name = ''
                try:
                    full = f"{getattr(creator, 'first_name', '') or ''} {getattr(creator, 'last_name', '') or ''}".strip()
                    if full:
                        creator_name = full
                    else:
                        creator_name = getattr(creator, 'username', '') or getattr(creator, 'email', '') or 'Пользователь'
                except Exception:
                    creator_name = getattr(creator, 'username', '') or getattr(creator, 'email', '') or 'Пользователь'

                for u in task.assignees.exclude(id=request.user.id):
                    if getattr(u, 'role', '').upper() != 'MANAGER':
                        continue
                    title = 'Новая задача'
                    msg_parts = []
                    if task.title:
                        msg_parts.append(task.title)
                    try:
                        when = task.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')
                        msg_parts.append(f"на {when}")
                    except Exception:
                        pass
                    # Добавляем информацию о постановщике
                    msg_parts.append(f"Поставил: {creator_name}")
                    msg = ' · '.join([p for p in msg_parts if p])
                    Notification.objects.create(
                        user=u,
                        task=task,
                        client=task.client if hasattr(task, 'client') else None,
                        title=title,
                        message=msg,
                        source='SYSTEM'
                    )
            except Exception:
                pass
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)
        # Разрешение редактирования:
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(task.client, 'created_by', None), 'company_id', None) if task.client else None
            client_user_company_id = getattr(getattr(task.client, 'user', None), 'company_id', None) if task.client else None
            created_by_company_id = getattr(getattr(task, 'created_by', None), 'company_id', None)
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id or created_by_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # MANAGER: может редактировать
            #  - свои задачи (created_by == self)
            #  - задачи по своим клиентам (client.created_by == self)
            #  - и задачи, где он находится в списке assignees
            can = False
            if not task.client:
                can = (task.created_by_id == request.user.id)
            else:
                if task.client.created_by_id == request.user.id:
                    can = True
            try:
                if not can and task.assignees.filter(id=request.user.id).exists():
                    can = True
            except Exception:
                pass
            if not can:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Если меняется клиент, проверим принадлежность
            new_client = serializer.validated_data.get('client')
            if new_client and new_client.created_by_id != request.user.id and role not in ('ADMIN','LEAD','LAWYER','ASSISTANT'):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
            task = serializer.save()
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Задача не найдена'}, status=status.HTTP_404_NOT_FOUND)
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            user_company_id = getattr(request.user, 'company_id', None)
            owner_company_id = getattr(getattr(task.client, 'created_by', None), 'company_id', None) if task.client else None
            client_user_company_id = getattr(getattr(task.client, 'user', None), 'company_id', None) if task.client else None
            created_by_company_id = getattr(getattr(task, 'created_by', None), 'company_id', None)
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id or created_by_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            if task.client:
                if task.client.created_by_id and task.client.created_by_id != request.user.id:
                    return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                if task.created_by_id != request.user.id:
                    return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UpcomingTasksWidgetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Q

        now = timezone.now()
        tz = timezone.get_current_timezone()
        local_now = timezone.localtime(now, tz)
        # Начало сегодняшнего дня (локально)
        start_today = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        # Превращаем обратно в aware (local_now уже aware)
        start_today_aware = start_today

        range_type = request.query_params.get('range', 'today')  # today | tomorrow | week | month

        if range_type == 'tomorrow':
            start_dt = start_today_aware + timedelta(days=1)
            end_dt = start_dt + timedelta(days=1)
        elif range_type == 'week':
            # Неделя вперёд начиная с текущего момента (включаем уже прошедшие сегодня события? нет – будущие/сегодняшние)
            start_dt = start_today_aware  # показываем и ранее начавшиеся сегодня задачи? фильтруем по start >= start of today
            end_dt = start_dt + timedelta(days=7)
        elif range_type == 'month':
            # До первого дня следующего месяца
            year = start_today_aware.year
            month = start_today_aware.month
            if month == 12:
                next_month_start = start_today_aware.replace(year=year + 1, month=1, day=1)
            else:
                next_month_start = start_today_aware.replace(month=month + 1, day=1)
            start_dt = start_today_aware
            end_dt = next_month_start
        else:  # today (по умолчанию)
            start_dt = start_today_aware
            end_dt = start_today_aware + timedelta(days=1)

        # Базовый QS: задачи в статусе SCHEDULED, стартующие в указанный интервал.
        # Для вкладки "today" теперь включаем задачи, которые уже начались утром (раньше now), т.к. критерий start >= start_of_day.
        base_qs = Task.objects.select_related('client', 'created_by').prefetch_related('assignees').filter(
            status='SCHEDULED',
            start__gte=start_dt,
            start__lt=end_dt
        )
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            user_company_id = getattr(request.user, 'company_id', None)
            if user_company_id:
                qs = base_qs.filter(
                    Q(client__created_by__company_id=user_company_id) |
                    Q(client__user__company_id=user_company_id) |
                    Q(client__isnull=True, created_by__company_id=user_company_id)
                )
            else:
                qs = base_qs.none()
        else:
            # Менеджер: свои или назначенные ему
            qs = base_qs.filter(
                Q(client__created_by=request.user) |
                Q(client__isnull=True, created_by=request.user) |
                Q(assignees=request.user)
            )
        limit = 100 if range_type in ('week', 'month') else 50
        try:
            qs = qs.order_by('start')[:limit]
            data = TaskListSerializer(qs, many=True).data
        except Exception:
            data = []
        return Response(data)


class FinanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ассистенту финансы недоступны — но на главной не валимся 500, возвращаем нулевую сводку с подсказкой
        if getattr(request.user, 'role', None) == 'ASSISTANT':
            return Response({'expected_payments_total': 0, 'expected_payments_month': 0, 'receipts_total': 0, 'receipts_month': 0, 'currency': 'PLN', 'month': timezone.now().strftime('%Y-%m'), 'detail': 'read_only'}, status=status.HTTP_200_OK)
        """
        Финансовая сводка для главной страницы.

        - expected_payments_total: сумма положительных балансов по своим клиентам.
        - expected_payments_month: сумма положительных балансов по своим клиентам,
          у которых есть хотя бы одно напоминание в текущем месяце (как приближение «сроки в этом месяце»).
        - receipts_total: суммарно получено (amount_paid) по своим клиентам — агрегатное значение.
        - receipts_month: пока 0 (нужна модель платежей с датами, чтобы корректно считать за период).
        """
        from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper
        from django.db.models.functions import Coalesce

        # Клиенты только текущего пользователя
        clients_qs = Client.objects.filter(created_by=request.user)

        # Баланс = service_cost - amount_paid (оба могут быть NULL) -> всегда Decimal
        dec0 = Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
        balances = clients_qs.annotate(
            balance=ExpressionWrapper(
                Coalesce(F('service_cost'), dec0) - Coalesce(F('amount_paid'), dec0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )
        expected_total = balances.filter(balance__gt=0).aggregate(
            total=Coalesce(Sum('balance'), dec0)
        )['total'] or 0

        # Текущий месяц
        now_local = timezone.localtime()
        start_month = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_month.month == 12:
            end_month = start_month.replace(year=start_month.year + 1, month=1)
        else:
            end_month = start_month.replace(month=start_month.month + 1)

        # Клиенты, у которых есть напоминания в этом месяце
        client_ids_with_rem = Reminder.objects.filter(
            client__created_by=request.user,
            reminder_date__gte=start_month.date(),
            reminder_date__lt=end_month.date(),
        ).values_list('client_id', flat=True).distinct()

        balances_month = balances.filter(id__in=client_ids_with_rem)
        expected_month = balances_month.filter(balance__gt=0).aggregate(
            total=Coalesce(Sum('balance'), dec0)
        )['total'] or 0

        # Поступления: без модели платежей считаем только агрегат total
        receipts_total = clients_qs.aggregate(total=Coalesce(Sum('amount_paid'), dec0))['total'] or 0
        receipts_month = 0  # Требуется модель Payment с датой для корректного подсчета за месяц

        try:
            payload = {
                'expected_payments_total': expected_total,
                'expected_payments_month': expected_month,
                'receipts_total': receipts_total,
                'receipts_month': receipts_month,
                'currency': 'PLN',
                'month': start_month.strftime('%Y-%m')
            }
        except Exception:
            payload = {'expected_payments_total': 0, 'expected_payments_month': 0, 'receipts_total': 0, 'receipts_month': 0, 'currency': 'PLN', 'month': timezone.now().strftime('%Y-%m')}
        return Response(payload)

# --- Уведомления ---
class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Проверка схемы БД: если новые поля (visible_at / scheduled_for) отсутствуют — вернём явную подсказку вместо 500
        from django.db import connection, OperationalError
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT visible_at, scheduled_for FROM crm_app_notification LIMIT 1")
        except OperationalError:
            return Response({
                'detail': 'Database migration missing for Notification (run manage.py migrate).',
                'hint': 'Apply latest migrations: python manage.py migrate'
            }, status=503)

        # Видимость: MANAGER видит только свои. ADMIN/LEAD/LAWYER/ASSISTANT видят все уведомления сотрудников своей компании.
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and request.user.company_id:
            qs = Notification.objects.filter(user__company_id=request.user.company_id)
            # Never show notifications about tasks created by the current user.
            # If the DB schema doesn't have task_id yet (no migration), skip the exclude gracefully.
            try:
                from django.db import connection
                with connection.cursor() as cur:
                    cur.execute("SELECT task_id FROM crm_app_notification LIMIT 1")
                qs = qs.exclude(task__created_by=request.user)
            except Exception:
                pass
        else:
            qs = Notification.objects.filter(user=request.user)
        # Одноразовое сидирование из Reminder, если ещё не делали
        try:
            user = request.user
            if not getattr(user, 'reminder_notifications_seeded', False):
                role = getattr(user, 'role', None)
                if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and user.company_id:
                    r_qs = Reminder.objects.select_related('client').filter(
                        models.Q(client__created_by__company_id=user.company_id) |
                        models.Q(client__user__company_id=user.company_id)
                    )
                else:
                    r_qs = Reminder.objects.select_related('client').filter(client__created_by=user)
                batch = []
                for r in r_qs[:1000]:
                    if Notification.objects.filter(user=user, reminder=r).exists():
                        continue
                    # Пропускаем напоминания, у которых плановое время уже в прошлом
                    try:
                        if r.reminder_date:
                            base_time = r.reminder_time or timezone.datetime.min.time()
                            sched_dt_tmp = timezone.make_aware(timezone.datetime.combine(r.reminder_date, base_time), timezone.get_current_timezone())
                            if sched_dt_tmp < timezone.now():
                                continue
                    except Exception:
                        pass
                    title = f"Напоминание: {r.get_reminder_type_display()}"
                    date_part = str(r.reminder_date) if r.reminder_date else ''
                    time_part = r.reminder_time.strftime('%H:%M') if r.reminder_time else ''
                    msg = (date_part + (' ' + time_part if time_part else '')).strip()
                    # Рассчитываем плановое время
                    scheduled_dt = None
                    try:
                        if r.reminder_date:
                            base = timezone.datetime.combine(r.reminder_date, r.reminder_time or timezone.datetime.min.time())
                            scheduled_dt = timezone.make_aware(base, timezone.get_current_timezone())
                    except Exception:
                        scheduled_dt = None
                    batch.append(Notification(
                        user=user,
                        client=r.client,
                        reminder=r,
                        title=title[:200],
                        message=msg,
                        source='REMINDER',
                        visible_at=scheduled_dt,
                        scheduled_for=scheduled_dt
                    ))
                # Новая логика: больше не сидируем массово; только ответственный менеджер будет получать уведомление при фактической отправке.
                batch = []  # ничего не добавляем
                user.reminder_notifications_seeded = True
                user.save(update_fields=['reminder_notifications_seeded'])
                qs = Notification.objects.filter(user=user)
        except Exception:
            pass

        # Фильтр по непрочитанным ?unread=1
        unread = request.query_params.get('unread')
        if unread == '1':
            qs = qs.filter(is_read=False)

        # Пагинация: ?limit=...&offset=...
        try:
            limit = int(request.query_params.get('limit', 500))
            if limit <= 0 or limit > 2000:
                limit = 500
        except Exception:
            limit = 500
        try:
            offset = int(request.query_params.get('offset', 0))
            if offset < 0:
                offset = 0
        except Exception:
            offset = 0

        qs = qs.order_by('-created_at')
        total = qs.count()
        sliced = qs[offset: offset + limit]
        ser = NotificationSerializer(sliced, many=True)
        return Response({'total': total, 'offset': offset, 'count': len(sliced), 'items': ser.data})

    def post(self, request):
        # возможность вручную создавать системные уведомления (для теста / внутреннего польз.)
        data = request.data.copy()
        data['user'] = request.user.id
        ser = NotificationSerializer(data=data)
        if ser.is_valid():
            obj = Notification.objects.create(
                user=request.user,
                title=ser.validated_data.get('title'),
                message=ser.validated_data.get('message', ''),
                source=ser.validated_data.get('source') or 'SYSTEM'
            )
            return Response(NotificationSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Для ролей, которые видят все уведомления компании, разрешаем отмечать прочитанным
        role = getattr(request.user, 'role', None)
        company_id = getattr(request.user, 'company_id', None)
        try:
            if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
                n = Notification.objects.get(pk=pk, user__company_id=company_id)
            else:
                n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        n.is_read = True
        n.save(update_fields=['is_read'])
        return Response({'detail': 'ok'})

class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = getattr(request.user, 'role', None)
        company_id = getattr(request.user, 'company_id', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
            # Отмечаем прочитанными ВСЕ уведомления компании (отражает то, что админ видит в списке),
            # исключая уведомления о задачах, поставленных текущим пользователем.
            qs = Notification.objects.filter(user__company_id=company_id, is_read=False)
            try:
                from django.db import connection
                with connection.cursor() as cur:
                    cur.execute("SELECT task_id FROM crm_app_notification LIMIT 1")
                qs = qs.exclude(task__created_by=request.user)
            except Exception:
                pass
            qs.update(is_read=True)
        else:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'ok'})

class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = getattr(request.user, 'role', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and request.user.company_id:
            qs = Notification.objects.filter(user__company_id=request.user.company_id, is_read=False)
            try:
                from django.db import connection
                with connection.cursor() as cur:
                    cur.execute("SELECT task_id FROM crm_app_notification LIMIT 1")
                qs = qs.exclude(task__created_by=request.user)
            except Exception:
                pass
            cnt = qs.count()
        else:
            cnt = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread': cnt})

class NotificationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        role = getattr(request.user, 'role', None)
        company_id = getattr(request.user, 'company_id', None)
        try:
            if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
                n = Notification.objects.get(pk=pk, user__company_id=company_id)
            else:
                n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        n.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NotificationBulkDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get('ids')
        if not isinstance(ids, list):
            return Response({'detail': 'ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        # Оставляем только целые числа
        clean_ids = []
        for i in ids:
            try:
                clean_ids.append(int(i))
            except Exception:
                continue
        if not clean_ids:
            return Response({'deleted': 0})
        role = getattr(request.user, 'role', None)
        company_id = getattr(request.user, 'company_id', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
            qs = Notification.objects.filter(user__company_id=company_id, id__in=clean_ids)
        else:
            qs = Notification.objects.filter(user=request.user, id__in=clean_ids)
        deleted = qs.count()
        qs.delete()
        return Response({'deleted': deleted})
