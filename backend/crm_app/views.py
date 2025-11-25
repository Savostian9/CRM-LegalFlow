from rest_framework.exceptions import ValidationError
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
from .models import Client, LegalCase, Document, Task, Reminder, Company, Invite, Notification, UploadedFile, UserPermissionSet
from .billing.plans import get_plan_limits, format_usage
from django.db.models import Sum
from .serializers import ClientListSerializer, ClientSerializer, LegalCaseSerializer, TaskSerializer, TaskListSerializer, \
    ProfileSerializer, ChangePasswordSerializer, CompanySerializer, UserAdminSerializer, InviteSerializer, NotificationSerializer, UploadedFileSerializer, UserPermissionSetSerializer
from urllib.parse import urlparse
from django.db.utils import OperationalError
from .limits import check_limit  # Import check_limit

def _check_user_permission(user, permission_flag: str) -> bool:
    """
    Check if user has a specific permission flag.
    ADMIN and LEAD roles have all permissions by default.
    Other roles check their UserPermissionSet.
    Returns True if permission is granted, False otherwise.
    """
    try:
        role = getattr(user, 'role', None)
        # ADMIN and LEAD always have full permissions
        if role in ('ADMIN', 'LEAD'):
            return True
        # Check UserPermissionSet for other roles
        try:
            permset = user.permset
            return getattr(permset, permission_flag, True)  # default True if field missing
        except UserPermissionSet.DoesNotExist:
            # No permission set means all permissions granted (backward compatibility)
            return True
    except Exception:
        # On any error, default to True to avoid breaking existing functionality
        return True

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

def _safe_send_mail(subject: str, body: str, to: list[str], html_body: str | None = None, user=None, company=None) -> bool:
    """Send mail with robust exception handling and optional HTML.
    Returns True if SMTP reports success, False otherwise.
    Prints diagnostic info when DEBUG is enabled.
    """
    from django.conf import settings
    success = False
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if html_body:
            from django.core.mail import EmailMultiAlternatives
            msg = EmailMultiAlternatives(subject, body, from_email, to)
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=False)
            success = True
        else:
            sent = send_mail(subject, body, from_email, to, fail_silently=False)
            success = bool(sent)
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

    if success and (user or company):
        try:
            from .models import SentEmail
            for recipient in to:
                SentEmail.objects.create(user=user, company=company, recipient=recipient, subject=subject)
        except Exception:
            pass
    return success


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

        # Use _safe_send_mail with user tracking
        _safe_send_mail(subject, text_body, [user.email], html_body=html_body, user=user)
    except Exception:
        # Fallback to a very simple mail in case templates or EmailMultiAlternatives fail
        try:
            subject = 'Подтверждение регистрации'
            _safe_send_mail(subject, f'Код подтверждения: {token}', [user.email], user=user)
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
from django.db.models.functions import TruncMonth
from collections import Counter

class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not getattr(user, 'is_superuser', False):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        # Companies (raw values, we'll filter out "deleted"/empty ones later)
        companies = Company.objects.all().values(
            'id', 'name', 'plan', 'created_at', 'trial_started_at', 'trial_ends_at', 'owner_id'
        )

        # Users and roles
        users_total = User.objects.count()
        users_by_role = (
            User.objects.values('role').annotate(count=Count('id')).order_by('role')
        )
        # For the admin dashboard: provide a compact list of users with last login info
        # Use annotate to alias related fields before extracting with values
        users_list = list(
            User.objects.select_related('company')
            .annotate(company_name=F('company__name'))
            .values(
                'id', 'username', 'email', 'first_name', 'last_name', 'role',
                'is_active', 'last_login', 'company_name', 'company_id'
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
            uc = counts_map.get(c['id'], 0)
            # Hide companies that have no owner and no users (e.g., owner deleted account and no one else remained)
            if not c['owner_id'] and uc == 0:
                continue
            companies_detail.append({
                'id': c['id'],
                'name': c['name'],
                'plan': c['plan'],
                'created_at': c['created_at'],
                'trial_started_at': c['trial_started_at'],
                'trial_ends_at': c['trial_ends_at'],
                'users_count': uc,
            })

        # Compute plans from filtered companies to avoid counting hidden/empty ones
        plan_counter = Counter(c['plan'] for c in companies_detail if c.get('plan'))
        plans = [{'plan': k, 'count': v} for k, v in sorted(plan_counter.items())]

        # Monthly stats (last 12 months): companies created and users registered
        try:
            now_ts = timezone.now()
            m_total = now_ts.year * 12 + (now_ts.month - 1)
            start_total = m_total - 11
            start_year = start_total // 12
            start_month = start_total % 12 + 1
            # Build timezone-aware start of month
            from datetime import datetime
            start_dt = datetime(start_year, start_month, 1, 0, 0, 0)
            start_aware = timezone.make_aware(start_dt, timezone.get_current_timezone())

            comp_qs = (
                Company.objects.filter(created_at__gte=start_aware)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            user_qs = (
                User.objects.filter(date_joined__gte=start_aware)
                .annotate(month=TruncMonth('date_joined'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
            comp_map = {}
            for row in comp_qs:
                try:
                    comp_map[row['month'].strftime('%Y-%m')] = row['count']
                except Exception:
                    comp_map[str(row['month'])[:7]] = row['count']
            user_map = {}
            for row in user_qs:
                try:
                    user_map[row['month'].strftime('%Y-%m')] = row['count']
                except Exception:
                    user_map[str(row['month'])[:7]] = row['count']

            monthly = []
            for i in range(12):
                cur_total = start_total + i
                y = cur_total // 12
                m = cur_total % 12 + 1
                label = f"{y}-{m:02d}"
                monthly.append({
                    'month': label,
                    'companies': int(comp_map.get(label, 0) or 0),
                    'users': int(user_map.get(label, 0) or 0),
                })
        except Exception:
            monthly = []

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
            'monthly': monthly,
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

class ProfilePermissionsView(APIView):
    """Get current user's permissions for frontend."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'role', None)
        # ADMIN and LEAD have all permissions
        if role in ('ADMIN', 'LEAD'):
            perms = {
                'can_create_client': True,
                'can_edit_client': True,
                'can_delete_client': True,
                'can_create_case': True,
                'can_edit_case': True,
                'can_delete_case': True,
                'can_create_task': True,
                'can_edit_task': True,
                'can_delete_task': True,
                'can_upload_files': True,
                'can_invite_users': True,
                'can_manage_users': True,
            }
        else:
            try:
                permset = user.permset
                perms = {
                    'can_create_client': permset.can_create_client,
                    'can_edit_client': permset.can_edit_client,
                    'can_delete_client': permset.can_delete_client,
                    'can_create_case': permset.can_create_case,
                    'can_edit_case': permset.can_edit_case,
                    'can_delete_case': permset.can_delete_case,
                    'can_create_task': permset.can_create_task,
                    'can_edit_task': permset.can_edit_task,
                    'can_delete_task': permset.can_delete_task,
                    'can_upload_files': permset.can_upload_files,
                    'can_invite_users': permset.can_invite_users,
                    'can_manage_users': permset.can_manage_users,
                }
            except UserPermissionSet.DoesNotExist:
                # Default to all permissions if no permission set exists
                perms = {
                    'can_create_client': True,
                    'can_edit_client': True,
                    'can_delete_client': True,
                    'can_create_case': True,
                    'can_edit_case': True,
                    'can_delete_case': True,
                    'can_create_task': True,
                    'can_edit_task': True,
                    'can_delete_task': True,
                    'can_upload_files': True,
                    'can_invite_users': True,
                    'can_manage_users': True,
                }
        return Response(perms)

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
            company = None

        # Удаляем пользователя
        request.user.delete()
        # Если у компании после удаления владельца не осталось пользователей — удаляем и компанию целиком,
        # чтобы она не "светилась" в админке как пустая/удаленная фирма
        try:
            if company and not User.objects.filter(company_id=getattr(company, 'id', None)).exists():
                company.delete()
        except Exception:
            pass
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
        if not _check_user_permission(request.user, 'can_manage_users'):
            return Response({'detail': 'У вас нет прав для управления пользователями'}, status=status.HTTP_403_FORBIDDEN)
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


class UserPermissionsAdminView(APIView):
    """Получение / обновление индивидуальных прав конкретного пользователя компании.
    GET: вернуть права (создаёт набор если отсутствует).
    PUT: обновить права (нельзя менять права владельца компании).
    Доступ: ADMIN / LEAD своей компании.
    """
    permission_classes = [IsAuthenticated]

    _flag_fields = [
        'can_create_client','can_edit_client','can_delete_client',
        'can_create_case','can_edit_case','can_delete_case',
        'can_create_task','can_edit_task','can_delete_task',
        'can_upload_files','can_invite_users','can_manage_users'
    ]

    def _ensure_permset(self, user: User) -> UserPermissionSet:
        ps, _ = UserPermissionSet.objects.get_or_create(user=user)
        return ps

    def get(self, request, pk):
        if request.user.role not in ('ADMIN','LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        company = getattr(request.user, 'company', None)
        if not company:
            return Response({'detail': 'Нет компании у текущего пользователя'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target = company.users.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            # Любая неожиданная ошибка — безопасный ответ
            try:
                import logging
                logging.getLogger(__name__).exception('UserPermissionsAdminView.get unexpected error')
            except Exception:
                pass
            from django.conf import settings as dj_settings
            if getattr(dj_settings, 'DEBUG', False):
                import sys, traceback
                et, ev, tb = sys.exc_info()
                return Response({'detail': 'internal_error', 'error_type': str(et), 'error': repr(ev)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'internal_error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            ps = self._ensure_permset(target)
            data = UserPermissionSetSerializer(ps).data
            data['user_id'] = target.id
            data['is_owner'] = (getattr(target.company, 'owner_id', None) == target.id)
            return Response(data)
        except Exception:
            try:
                import logging
                logging.getLogger(__name__).exception('UserPermissionsAdminView.get permset error')
            except Exception:
                pass
            from django.conf import settings as dj_settings
            if getattr(dj_settings, 'DEBUG', False):
                import sys
                et, ev, tb = sys.exc_info()
                return Response({'detail': 'internal_error', 'error_type': str(et), 'error': repr(ev)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'internal_error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        if request.user.role not in ('ADMIN','LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        try:
            target = request.user.company.users.get(pk=pk)
        except Exception:
            return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Защита владельца компании
        if getattr(target.company, 'owner_id', None) == target.id:
            return Response({'detail': 'Нельзя изменять права владельца'}, status=status.HTTP_400_BAD_REQUEST)

        def _parse_bool(val):
            # Корректно интерпретируем строки из JSON/формы
            if isinstance(val, bool):
                return val
            if val is None:
                return False
            if isinstance(val, (int, float)):
                return bool(val)
            s = str(val).strip().lower()
            if s in ('1','true','yes','y','on'): return True
            if s in ('0','false','no','n','off','', 'null', 'none'): return False
            return bool(val)
        try:
            ps = self._ensure_permset(target)
            changed = False
            for k in self._flag_fields:
                if k in request.data:
                    new_val = _parse_bool(request.data.get(k))
                    if getattr(ps, k) != new_val:
                        setattr(ps, k, new_val)
                        changed = True
            if changed:
                ps.save()
            data = UserPermissionSetSerializer(ps).data
            data['updated'] = changed
            return Response(data)
        except Exception as e:
            # Логируем и возвращаем управляемый ответ вместо 500 с HTML (особенно важно для фронта)
            try:
                import logging
                logging.getLogger(__name__).exception('UserPermissionsAdminView.put unexpected error')
            except Exception:
                pass
            from django.conf import settings as dj_settings
            if getattr(dj_settings, 'DEBUG', False):
                return Response({'detail': 'internal_error', 'error_type': str(type(e)), 'error': repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'internal_error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPermissionsBulkAdminView(APIView):
    """Массовое применение прав ко всем (или выбранным) пользователям компании.
    POST body:
      flags... (любой поднабор флагов)
      user_ids: optional list[int] - ограничить набор.
      exclude_owner: bool (default True)
    Возвращает: {'updated': N, 'total': M}
    """
    permission_classes = [IsAuthenticated]

    _flag_fields = UserPermissionsAdminView._flag_fields

    def post(self, request):
        if request.user.role not in ('ADMIN','LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        company = request.user.company
        if not company:
            return Response({'detail': 'Нет компании'}, status=status.HTTP_400_BAD_REQUEST)
        user_ids = request.data.get('user_ids')
        qs = company.users.all()
        if isinstance(user_ids, list):
            ints = [uid for uid in user_ids if isinstance(uid, int) or (isinstance(uid, str) and uid.isdigit())]
            ints = [int(i) for i in ints]
            if ints:
                qs = qs.filter(id__in=ints)
        exclude_owner = request.data.get('exclude_owner', True)
        owner_id = getattr(company, 'owner_id', None)
        if exclude_owner and owner_id:
            qs = qs.exclude(id=owner_id)
        flags = {k: bool(request.data.get(k)) for k in self._flag_fields if k in request.data}
        if not flags:
            return Response({'detail': 'Нет флагов для применения'}, status=status.HTTP_400_BAD_REQUEST)
        updated = 0
        for user in qs:
            ps, _ = UserPermissionSet.objects.get_or_create(user=user)
            changed = False
            for k,v in flags.items():
                if getattr(ps, k) != v:
                    setattr(ps, k, v)
                    changed = True
            if changed:
                ps.save()
                updated += 1
        return Response({'updated': updated, 'total': qs.count(), 'applied_flags': list(flags.keys())})

class UserDetailAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if not getattr(request.user, 'is_superuser', False) and request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        try:
            if getattr(request.user, 'is_superuser', False):
                user = User.objects.get(pk=pk)
            else:
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
        if not getattr(request.user, 'is_superuser', False) and request.user.role not in ('ADMIN', 'LEAD'):
            return Response({'detail': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)
        try:
            if getattr(request.user, 'is_superuser', False):
                user = User.objects.get(pk=pk)
            else:
                user = request.user.company.users.get(pk=pk)
        except Exception:
            return Response({'detail': 'Не найден'}, status=status.HTTP_404_NOT_FOUND)
        # Нельзя удалить самого себя
        if user.id == request.user.id:
            return Response({'detail': 'Нельзя удалить собственный аккаунт из этой формы'}, status=status.HTTP_400_BAD_REQUEST)
        # Если удаляем владелца компании — отвяжем и при необходимости удалим пустую компанию
        try:
            company = getattr(user, 'owned_company', None)
            if company:
                company.owner = None
                company.save()
        except Exception:
            company = None
        user.delete()
        try:
            if company and not User.objects.filter(company_id=getattr(company, 'id', None)).exists():
                company.delete()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- Приглашения ---
class InviteCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Проверка лимита пользователей (включая активные приглашения)
        check_limit(request.user, 'users')

        # Check permission
        if not _check_user_permission(request.user, 'can_invite_users'):
            return Response({'detail': 'У вас нет прав для создания приглашений'}, status=status.HTTP_403_FORBIDDEN)
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
        
        # Проверяем лимит пользователей перед принятием приглашения
        from .limits import check_limit
        try:
            # Проверяем лимит для компании пригласившего (или владельца приглашения)
            check_limit(invite.created_by, 'users')
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

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
            # Суммарный вес
            total_storage_mb = 0
            try:
                total_bytes = UploadedFile.objects.filter(document__in=files_qs).aggregate(s=Sum('file_size'))['s'] or 0
                total_storage_mb = round(total_bytes / (1024 * 1024), 2)
            except Exception:
                total_storage_mb = 0
        except Exception:
            total_storage_mb = 0

        # Tasks за текущий год (по запросу пользователя лимиты годовые)
        now = timezone.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        tasks_month = Task.objects.filter(
            models.Q(client__in=Client.objects.filter(
                models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
            )) |
            models.Q(created_by__company_id=company.id),
            created_at__gte=year_start
        ).distinct().count() if hasattr(Task, 'created_at') else 0

        # Active reminders (sent_at is null)
        reminders_active = Reminder.objects.filter(
            client__in=Client.objects.filter(
                models.Q(created_by__company_id=company.id) | models.Q(user__company_id=company.id)
            ),
            sent_at__isnull=True
        ).count()

        # Emails per month (пока нет лога — 0)
        emails_month = 0
        try:
            from .models import SentEmail
            emails_month = SentEmail.objects.filter(
                models.Q(company=company) | models.Q(user__company=company),
                sent_at__gte=year_start
            ).count()
        except Exception:
            pass

        raw_usage = {
            'users': users_count,
            'clients': clients_count,
            'cases': cases_count,
            'files': files_count,
            'files_storage_mb': total_storage_mb,
            'tasks_per_month': tasks_month,
            'reminders_active': reminders_active,
            'emails_per_month': emails_month,
        }
        formatted = format_usage(limits, raw_usage)

        payment_method_info = None
        if company.stripe_customer_id:
            try:
                import stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                customer = stripe.Customer.retrieve(
                    company.stripe_customer_id, 
                    expand=['invoice_settings.default_payment_method']
                )
                pm = customer.invoice_settings.default_payment_method
                if pm and isinstance(pm, dict):
                    card = pm.get('card', {})
                    payment_method_info = {
                        'brand': card.get('brand'),
                        'last4': card.get('last4'),
                        'exp_month': card.get('exp_month'),
                        'exp_year': card.get('exp_year'),
                    }
            except Exception:
                pass

        return Response({
            'plan': plan_code,
            'stripe_customer_id': company.stripe_customer_id,
            'limits': limits,
            'usage': formatted,
            'payment_method': payment_method_info,
            'trial': {
                'started_at': trial_started,
                'ends_at': trial_ends,
                'days_left': trial_days_left,
                'expired': trial_expired,
            },
            'read_only': trial_expired and plan_code == 'TRIAL'
        })

class BillingUpgradeView(APIView):
    """Endpoint переключения плана (временный, без оплаты).
    Поддерживаемые сценарии:
      - TRIAL -> STARTER | PRO
      - STARTER -> PRO
      - PRO -> STARTER (даунгрейд)
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
        allowed_map = {
            'TRIAL': {'STARTER', 'PRO'},
            'STARTER': {'PRO'},
            'PRO': {'STARTER'},
        }
        allowed_targets = allowed_map.get(current, set())
        if target not in allowed_targets:
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
        # Проверка лимита клиентов
        check_limit(request.user, 'clients')

        # Check permission
        if not _check_user_permission(request.user, 'can_create_client'):
            return Response({'detail': 'У вас нет прав для создания клиентов'}, status=status.HTTP_403_FORBIDDEN)
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
        serializer = ClientSerializer(data=data, context={'request': request})
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
        # Check permission
        if not _check_user_permission(request.user, 'can_edit_client'):
            return Response({'detail': 'У вас нет прав для редактирования клиентов'}, status=status.HTTP_403_FORBIDDEN)
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
            serializer = ClientSerializer(client, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Удаление клиента.
        Правила доступа:
        - ADMIN / LEAD / LAWYER могут удалять клиента своей компании (по created_by.company или client.user.company)
        - MANAGER может удалить только своих клиентов (created_by == self)
        - ASSISTANT не может удалять
        # Check permission
        if not _check_user_permission(request.user, 'can_delete_client'):
            return Response({'detail': 'У вас нет прав для удаления клиентов'}, status=status.HTTP_403_FORBIDDEN)
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
        # Проверка лимита дел
        check_limit(request.user, 'cases')

        # Check permission
        if not _check_user_permission(request.user, 'can_create_case'):
            return Response({'detail': 'У вас нет прав для создания дел'}, status=status.HTTP_403_FORBIDDEN)
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
            import re
            # Use regex for case-insensitive search (supports Cyrillic in SQLite)
            pattern = re.escape(search)
            qs = qs.filter(
                models.Q(title__iregex=pattern) | 
                models.Q(description__iregex=pattern) |
                models.Q(client__first_name__iregex=pattern) |
                models.Q(client__last_name__iregex=pattern) |
                models.Q(assignees__first_name__iregex=pattern) |
                models.Q(assignees__last_name__iregex=pattern) |
                models.Q(assignees__username__iregex=pattern)
            ).distinct()
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
        # Проверка лимита задач (в месяц)
        check_limit(request.user, 'tasks_per_month')

        # Check permission
        if not _check_user_permission(request.user, 'can_create_task'):
            return Response({'detail': 'У вас нет прав для создания задач'}, status=status.HTTP_403_FORBIDDEN)
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
                pass            # Создаём уведомления для всех назначенных исполнителей (кроме автора)
            try:
                # Подготовим имя постановщика задачи (создателя)
                creator = request.user
                # Отображаемое имя: Имя Фамилия -> Компания -> Email/логин
                try:
                    first = (getattr(creator, 'first_name', '') or '').strip()
                    last = (getattr(creator, 'last_name', '') or '').strip()
                    full = f"{first} {last}".strip()
                    if full:
                        creator_name = full
                    else:
                        company_name = (getattr(getattr(creator, 'company', None), 'name', '') or '').strip()
                        creator_name = company_name or getattr(creator, 'email', '') or getattr(creator, 'username', '') or 'Пользователь'
                except Exception:
                    creator_name = getattr(creator, 'email', '') or getattr(creator, 'username', '') or 'Пользователь'

                # Определяем язык из заголовков запроса
                def _pref_lang(req):
                    try:
                        x = (req.META.get('HTTP_X_LOCALE') or '').lower()
                        if x.startswith('pl'):
                            return 'pl'
                        if x.startswith('ru'):
                            return 'ru'
                        if x.startswith('en'):
                            return 'en'
                        al = (req.META.get('HTTP_ACCEPT_LANGUAGE') or '').lower()
                        if 'pl' in al:
                            return 'pl'
                        if 'ru' in al:
                            return 'ru'
                        return 'en'
                    except Exception:
                        return 'en'

                lang = _pref_lang(request)
                if lang == 'pl':
                    title_loc = 'Nowe zadanie'
                    when_label = 'na'
                    created_by_label = 'Utworzył'
                elif lang == 'ru':
                    title_loc = 'Новая задача'
                    when_label = 'на'
                    created_by_label = 'Поставил'
                else:
                    title_loc = 'New task'
                    when_label = 'on'
                    created_by_label = 'Created by'

                for u in task.assignees.exclude(id=request.user.id):
                    title = title_loc
                    msg_parts = []
                    if task.title:
                        msg_parts.append(task.title)
                    try:
                        when = task.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')
                        msg_parts.append(f"{when_label} {when}")
                    except Exception:
                        pass
                    # Добавляем информацию о постановщике
                    msg_parts.append(f"{created_by_label}: {creator_name}")
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

    def get(self, request, pk):
        """Return full task details for the provided id.
        Visibility rules mirror update/delete: company-scoped for admin roles,
        and creator/assignee-based for managers. This endpoint enables
        dashboards to fetch complete fields (location/description, etc.).
        """
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
            # MANAGER visibility: own tasks, tasks for own clients, or where listed as assignee
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

        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        # Check permission
        if not _check_user_permission(request.user, 'can_edit_task'):
            return Response({'detail': 'У вас нет прав для редактирования задач'}, status=status.HTTP_403_FORBIDDEN)
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
        # Сохраним текущий список исполнителей, чтобы понять, кого добавили при обновлении
        try:
            old_assignees = set(task.assignees.values_list('id', flat=True))
        except Exception:
            old_assignees = set()

        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Если меняется клиент, проверим принадлежность
            new_client = serializer.validated_data.get('client')
            if new_client and new_client.created_by_id != request.user.id and role not in ('ADMIN','LEAD','LAWYER','ASSISTANT'):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
            task = serializer.save()

            # После сохранения проверим, появились ли новые исполнители — уведомим их
            try:
                new_assignees = set(task.assignees.values_list('id', flat=True))
                added_ids = [aid for aid in new_assignees if aid not in old_assignees and aid != request.user.id]
                if added_ids:
                    # Имя постановщика (кто выполнял обновление)
                    updater = request.user
                    try:
                        first = (getattr(updater, 'first_name', '') or '').strip()
                        last = (getattr(updater, 'last_name', '') or '').strip()
                        full = f"{first} {last}".strip()
                        if full:
                            updater_name = full
                        else:
                            company_name = (getattr(getattr(updater, 'company', None), 'name', '') or '').strip()
                            updater_name = company_name or getattr(updater, 'email', '') or getattr(updater, 'username', '') or 'Пользователь'
                    except Exception:
                        updater_name = getattr(updater, 'email', '') or getattr(updater, 'username', '') or 'Пользователь'

                    # Определяем язык из заголовков запроса
                    def _pref_lang(req):
                        try:
                            x = (req.META.get('HTTP_X_LOCALE') or '').lower()
                            if x.startswith('pl'):
                                return 'pl'
                            if x.startswith('ru'):
                                return 'ru'
                            if x.startswith('en'):
                                return 'en'
                            al = (req.META.get('HTTP_ACCEPT_LANGUAGE') or '').lower()
                            if 'pl' in al:
                                return 'pl'
                            if 'ru' in al:
                                return 'ru'
                            return 'en'
                        except Exception:
                            return 'en'

                    lang = _pref_lang(request)
                    if lang == 'pl':
                        title_loc = 'Zadanie przypisane'
                        when_label = 'na'
                        assigned_by_label = 'Przypisał'
                    elif lang == 'ru':
                        title_loc = 'Задача назначена'
                        when_label = 'на'
                        assigned_by_label = 'Назначил'
                    else:
                        title_loc = 'Task assigned'
                        when_label = 'on'
                        assigned_by_label = 'Assigned by'

                    from .models import User as _User
                    for u in _User.objects.filter(id__in=added_ids):
                        title = title_loc
                        msg_parts = []
                        if task.title:
                            msg_parts.append(task.title)
                        try:
                            when = task.start.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M')
                            msg_parts.append(f"{when_label} {when}")
                        except Exception:
                            pass
                        msg_parts.append(f"{assigned_by_label}: {updater_name}")
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

            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Check permission
        if not _check_user_permission(request.user, 'can_delete_task'):
            return Response({'detail': 'У вас нет прав для удаления задач'}, status=status.HTTP_403_FORBIDDEN)
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
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and request.user.company_id:
            # Видимость: задачи по клиентам своей компании или личные задачи сотрудников компании
            qs = base_qs.filter(
                models.Q(client__created_by__company_id=request.user.company_id) |
                models.Q(client__user__company_id=request.user.company_id) |
                models.Q(client__isnull=True, created_by__company_id=request.user.company_id)
            )
        else:
            # Менеджер: свои или назначенные ему
            qs = base_qs.filter(
                models.Q(client__created_by=request.user) |
                models.Q(client__isnull=True, created_by=request.user) |
                models.Q(assignees=request.user)
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
            end_month = start_month.replace(year=start_month.year + 1, month=1, day=1)
        else:
            end_month = start_month.replace(month=start_month.month + 1, day=1)

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
        company_id = getattr(request.user, 'company_id', None)
        # ВАЖНО: уведомления по напоминаниям (source='REMINDER') видит только тот менеджер, к которому привязан клиент (user=request.user).
        # Для остальных источников (SYSTEM) админские роли видят по компании, как и раньше.
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
            qs = Notification.objects.filter(
                (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
            )
            # Не показываем уведомления о задачах, поставленных текущим пользователем
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
        ser = NotificationSerializer(sliced, many=True, context={'request': request})
        items = list(ser.data)
        # Локализация заголовков/сообщений REMINDER для польского интерфейса
        try:
            # Определяем язык из заголовков
            def _pref_lang(req):
                try:
                    x = (req.META.get('HTTP_X_LOCALE') or '').lower()
                    if x.startswith('pl'):
                        return 'pl'
                    if x.startswith('ru'):
                        return 'ru'
                    if x.startswith('en'):
                        return 'en'
                    al = (req.META.get('HTTP_ACCEPT_LANGUAGE') or '').lower()
                    if 'pl' in al:
                        return 'pl'
                    if 'ru' in al:
                        return 'ru'
                    return 'en'
                except Exception:
                    return 'en'
            lang = _pref_lang(request)
            if lang == 'pl':
                def tr_title(t: str) -> str:
                    if not isinstance(t, str):
                        return t
                    return (
                        t.replace('Напоминание', 'Przypomnienie')
                         .replace('отправлено', 'wysłano')
                         .replace('ОШИБКА отправки email', 'BŁĄD wysyłki email')
                         .replace('нет email у клиента', 'brak emailu klienta')
                    )
                def tr_msg(m: str) -> str:
                    if not isinstance(m, str):
                        return m
                    return m.replace('Клиент:', 'Klient:')
                for it in items:
                    try:
                        if it.get('source') == 'REMINDER':
                            it['title'] = tr_title(it.get('title'))
                            it['message'] = tr_msg(it.get('message'))
                    except Exception:
                        continue
        except Exception:
            pass
        return Response({'total': total, 'offset': offset, 'count': len(items), 'items': items})

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
        # Админские роли не могут помечать REMINDER для других пользователей
        role = getattr(request.user, 'role', None)
        company_id = getattr(request.user, 'company_id', None)
        try:
            if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
                qs = Notification.objects.filter(
                    (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                    (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
                )
                n = qs.get(pk=pk)
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
            # Отмечаем прочитанными только те уведомления, которые админ действительно видит (REMINDER только свои)
            qs = Notification.objects.filter(is_read=False).filter(
                (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
            )
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
        company_id = getattr(request.user, 'company_id', None)
        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT') and company_id:
            qs = Notification.objects.filter(is_read=False).filter(
                (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
            )
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
                qs = Notification.objects.filter(
                    (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                    (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
                )
                n = qs.get(pk=pk)
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
            qs = Notification.objects.filter(id__in=clean_ids).filter(
                (models.Q(source='REMINDER') & models.Q(user=request.user)) |
                (~models.Q(source='REMINDER') & models.Q(user__company_id=company_id))
            )
        else:
            qs = Notification.objects.filter(user=request.user, id__in=clean_ids)
        deleted = qs.count()
        qs.delete()
        return Response({'deleted': deleted})

# --- Загрузка и удаление файлов документов ---
class DocumentFileUploadView(APIView):
    """Загрузка одного или нескольких файлов к документу.
    Принимает multipart/form-data с ключом 'file' (один файл) или 'files' (несколько файлов).
    Дополнительно поддерживает поле 'description'.

    Права доступа:
    - ADMIN/LEAD/LAWYER/ASSISTANT: документ клиента своей компании
    - MANAGER: документ клиента, которого он создал (created_by == self)
    - ASSISTANT может загружать, если принадлежит той же компании (как выше)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        # Проверка лимитов файлов и хранилища
        check_limit(request.user, 'files')
        check_limit(request.user, 'files_storage_mb')

        # Check permission
        if not _check_user_permission(request.user, 'can_upload_files'):
            return Response({'detail': 'У вас нет прав для загрузки файлов.'}, status=status.HTTP_403_FORBIDDEN)

        # Находим документ
        try:
            doc = Document.objects.select_related('legal_case__client__created_by', 'legal_case__client__user').get(pk=document_id)
        except Document.DoesNotExist:
            return Response({'detail': 'Документ не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем права
        role = getattr(request.user, 'role', None)
        user_company_id = getattr(request.user, 'company_id', None)
        owner_company_id = getattr(getattr(getattr(doc.legal_case.client, 'created_by', None), 'company', None), 'id', None)
        client_user_company_id = getattr(getattr(getattr(doc.legal_case.client, 'user', None), 'company', None), 'id', None)

        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # MANAGER: только для своих клиентов
            if getattr(doc.legal_case.client, 'created_by_id', None) != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        # Получаем файлы из запроса
        files = request.FILES.getlist('files') or []
        if not files:
            f = request.FILES.get('file')
            if f:
                files = [f]
        if not files:
            return Response({'detail': 'Файл не передан'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Проверка лимита с учетом размера загружаемых файлов ---
        try:
            incoming_size_mb = sum(f.size for f in files) / (1024 * 1024)
            user = request.user
            if user and user.company:
                from .models import PLAN_LIMITS
                company = user.company
                plan = company.plan or 'TRIAL'
                limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['TRIAL'])
                limit_mb = limits.get('files_storage_mb')
                
                if limit_mb is not None:
                    # Считаем текущее использование
                    total_bytes = UploadedFile.objects.filter(
                        models.Q(document__legal_case__client__created_by__company=company) | 
                        models.Q(document__legal_case__client__user__company=company)
                    ).distinct().aggregate(Sum('file_size'))['file_size__sum'] or 0
                    current_mb = total_bytes / (1024 * 1024)
                    
                    if current_mb + incoming_size_mb > limit_mb:
                        from django.utils.translation import get_language
                        lang = get_language()
                        if lang and lang.lower().startswith('pl'):
                            msg = f'Przekroczono limit pamięci. Limit: {limit_mb} MB, Obecnie: {int(current_mb)} MB, Przesyłanie: {int(incoming_size_mb)} MB. Zaktualizuj plan.'
                        else:
                            msg = f'Превышен лимит хранилища. Лимит: {limit_mb} МБ, Текущее: {int(current_mb)} МБ, Загрузка: {int(incoming_size_mb)} МБ. Обновите тариф.'

                        return Response({
                            'detail': msg
                        }, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            pass
        # -----------------------------------------------------------

        description = request.data.get('description', '')

        created = []
        for f in files:
            try:
                uf = UploadedFile.objects.create(document=doc, file=f, description=description or '')
                created.append(uf)
            except Exception as e:
                return Response({'detail': 'Ошибка сохранения файла', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = UploadedFileSerializer(created, many=True, context={'request': request}).data
        # После загрузки пометим документ "SUBMITTED", если были файлы
        try:
            if created and getattr(doc, 'status', None) == 'NOT_SUBMITTED':
                doc.status = 'SUBMITTED'
                doc.save(update_fields=['status'])
        except Exception:
            pass
        # Если передан один файл — вернем объект, иначе список
        if len(data) == 1:
            return Response(data[0], status=status.HTTP_201_CREATED)
        return Response(data, status=status.HTTP_201_CREATED)


class UploadedFileDeleteView(APIView):
    """Удаление загруженного файла документа (и физического файла)."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # Check permission
        if not _check_user_permission(request.user, 'can_upload_files'):
            return Response({'detail': 'У вас нет прав для управления файлами.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            uf = UploadedFile.objects.select_related('document__legal_case__client__created_by', 'document__legal_case__client__user').get(pk=pk)
        except UploadedFile.DoesNotExist:
            return Response({'detail': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)

        doc = uf.document
        role = getattr(request.user, 'role', None)
        user_company_id = getattr(request.user, 'company_id', None)
        owner_company_id = getattr(getattr(getattr(doc.legal_case.client, 'created_by', None), 'company', None), 'id', None)
        client_user_company_id = getattr(getattr(getattr(doc.legal_case.client, 'user', None), 'company', None), 'id', None)

        if role in ('ADMIN', 'LEAD', 'LAWYER', 'ASSISTANT'):
            if not (user_company_id and (owner_company_id == user_company_id or client_user_company_id == user_company_id)):
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # MANAGER: только для своих клиентов
            if getattr(doc.legal_case.client, 'created_by_id', None) != request.user.id:
                return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Удаляем файл
            uf.delete()
            # Если не осталось файлов у документа — можно сбросить статус на NOT_SUBMITTED
            try:
                if not uf.document.files.exists() and getattr(uf.document, 'status', None) == 'SUBMITTED':
                    uf.document.status = 'NOT_SUBMITTED'
                    uf.document.save(update_fields=['status'])
            except Exception:
                pass
        except Exception as e:
            return Response({'detail': 'Ошибка удаления файла', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
