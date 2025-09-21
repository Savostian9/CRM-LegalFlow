# backend/crm_app/urls.py

from django.urls import path
from .views import (
    RegisterRequestView,
    VerifyEmailView,
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    UserInfoView,
    ResendVerificationEmailView,
    ClientListView,
    ClientDetailView,
    CaseCreateView    
)

urlpatterns = [
    path('register/', RegisterRequestView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('resend-verify-email/', ResendVerificationEmailView.as_view(), name='resend-verify-email'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:client_pk>/cases/', CaseCreateView.as_view(), name='case-create'),
]