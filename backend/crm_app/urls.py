# backend/crm_app/urls.py

from django.urls import path
from .views import (
    RegisterRequestView,
    VerifyEmailView,
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    UserInfoView,
    ProfileView,
    ChangePasswordView,
    DeleteAccountView,
    ResendVerificationEmailView,
    ClientListView,
    ClientDetailView,
    CaseCreateView,
    TaskListCreateView,
    TaskDetailView,
    UpcomingTasksWidgetView,
    FinanceSummaryView,
    CompanySettingsView,
    UsersAdminView,
    UserDetailAdminView,
    InviteCreateView,
    InviteAcceptView    
)
from .views import NotificationListCreateView, NotificationMarkReadView, NotificationMarkAllReadView, NotificationUnreadCountView, NotificationDeleteView, NotificationBulkDeleteView, BillingUsageView, BillingUpgradeView

urlpatterns = [
    path('register/', RegisterRequestView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('resend-verify-email/', ResendVerificationEmailView.as_view(), name='resend-verify-email'),
    # Компания и пользователи
    path('company/settings/', CompanySettingsView.as_view(), name='company-settings'),
    path('company/users/', UsersAdminView.as_view(), name='company-users'),
    path('company/users/<int:pk>/', UserDetailAdminView.as_view(), name='company-user-detail'),
    path('company/invites/', InviteCreateView.as_view(), name='invite-create'),
    path('company/invites/accept/', InviteAcceptView.as_view(), name='invite-accept'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:client_pk>/cases/', CaseCreateView.as_view(), name='case-create'),
    # Задачи / календарь
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/upcoming/', UpcomingTasksWidgetView.as_view(), name='tasks-upcoming'),
    # Финансы
    path('finance/summary/', FinanceSummaryView.as_view(), name='finance-summary'),
    # Уведомления
    path('notifications/', NotificationListCreateView.as_view(), name='notifications'),
    path('notifications/mark-read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('notifications/<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
    path('notifications/bulk-delete/', NotificationBulkDeleteView.as_view(), name='notification-bulk-delete'),
    # Billing / usage
    path('billing/usage/', BillingUsageView.as_view(), name='billing-usage'),
    path('billing/upgrade/', BillingUpgradeView.as_view(), name='billing-upgrade'),
]