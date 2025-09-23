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
from .serializers import UserRegistrationSerializer
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
from .models import Client, LegalCase, Document
from .serializers import ClientListSerializer, ClientSerializer, LegalCaseSerializer




class RegisterRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_client=True) # Создаем пользователя-клиента
            token = ''.join(random.choices('0123456789', k=6))
            EmailVerificationToken.objects.create(user=user, token=token)

            # Отправка email (нужно настроить Django для отправки почты)
            subject = 'Подтверждение регистрации'
            message = f'Ваш код подтверждения: {token}'
            send_mail(
                subject,
                message,
                'noreply@yourdomain.com', # <--- Замените на свой email
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Код подтверждения отправлен на ваш email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')

        if not email or not token:
            return Response({'error': 'Email и токен обязательны.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            verification_token = EmailVerificationToken.objects.get(user=user, token=token)

            # ПРОВЕРКА: если прошло больше 5 минут, код недействителен
            if timezone.now() > verification_token.created_at + timedelta(minutes=5):
                verification_token.delete()
                return Response({'error': 'Срок действия кода истёк.'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()
            verification_token.delete()
            return Response({'message': 'Регистрация успешно завершена!'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Неверный токен.'}, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обязателен.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь с таким email не найден.'}, status=status.HTTP_404_NOT_FOUND)

        form = PasswordResetForm({'email': user.email})
        if form.is_valid():
            subject = 'Сброс пароля для вашей CRM-системы'
            # Здесь мы создаем ссылку сброса, которая будет вести на фронтенд
            context = {
                'email': user.email,
                'domain': 'localhost:8080',  # <--- Замените на домен вашего фронтенда
                'site_name': 'CRM LegalFlow',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            # Это просто пример текста, который будет в письме
            message = f"Здравствуйте, {user.username}. Пожалуйста, перейдите по следующей ссылке для сброса пароля: http://{context['domain']}/password-reset/confirm/{context['uid']}/{context['token']}/"
            
            send_mail(
                subject,
                message,
                'noreply@yourdomain.com', # <--- Ваш email
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Ссылка для сброса пароля отправлена на ваш email.'}, status=status.HTTP_200_OK)
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
            'email': user.email
        })
    
class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            # Удаляем старый токен, если он был
            EmailVerificationToken.objects.filter(user=user).delete()

            # Создаем и отправляем новый
            token = ''.join(random.choices('0123456789', k=6))
            EmailVerificationToken.objects.create(user=user, token=token)

            subject = 'Новый код подтверждения'
            message = f'Ваш новый код подтверждения: {token}'
            send_mail(subject, message, 'noreply@yourdomain.com', [user.email])

            return Response({'message': 'Новый код отправлен на ваш email.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден или уже активен.'}, status=status.HTTP_404_NOT_FOUND)
        
class ClientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientListSerializer(clients, many=True)
        return Response(serializer.data)

    # ДОБАВЛЯЕМ МЕТОД POST
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            # Здесь в будущем можно будет привязать клиента к менеджеру (request.user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
            serializer = ClientSerializer(client)
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            serializer = ClientSerializer(client, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CaseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_pk):
        try:
            client = Client.objects.get(pk=client_pk)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LegalCaseSerializer(data=request.data)
        if serializer.is_valid():
            # При сохранении передаем клиента, чтобы связать с ним дело
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
