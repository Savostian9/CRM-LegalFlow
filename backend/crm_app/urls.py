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
    ProfilePermissionsView,
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
    InviteAcceptView,   
    UserPermissionsAdminView,
    UserPermissionsBulkAdminView    
)
from .views import AdminStatsView
from .views import NotificationListCreateView, NotificationMarkReadView, NotificationMarkAllReadView, NotificationUnreadCountView, NotificationDeleteView, NotificationBulkDeleteView, BillingUsageView, DocumentFileUploadView, UploadedFileDeleteView
from crm_app.billing.views import (
    CreateCheckoutSessionView, 
    stripe_webhook, 
    CreateCustomerPortalSessionView, 
    CancelSubscriptionView,
    ChangePlanView,
    StripeConfigView,
    CreateSetupIntentView,
    UpdateDefaultPaymentMethodView
)

urlpatterns = [
    path('register/', RegisterRequestView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
        path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/permissions/', ProfilePermissionsView.as_view(), name='profile-permissions'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    path('resend-verify-email/', ResendVerificationEmailView.as_view(), name='resend-verify-email'),
    # Компания и пользователи
    path('company/settings/', CompanySettingsView.as_view(), name='company-settings'),
    path('company/users/', UsersAdminView.as_view(), name='company-users'),
    path('company/users/<int:pk>/', UserDetailAdminView.as_view(), name='company-user-detail'),
    path('company/users/<int:pk>/permissions/', UserPermissionsAdminView.as_view(), name='company-user-permissions'),
    path('company/users/permissions/bulk/', UserPermissionsBulkAdminView.as_view(), name='company-user-permissions-bulk'),
    path('company/invites/', InviteCreateView.as_view(), name='invite-create'),
    path('company/invites/accept/', InviteAcceptView.as_view(), name='invite-accept'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:client_pk>/cases/', CaseCreateView.as_view(), name='case-create'),
    # Документы / файлы
    path('documents/<int:document_id>/files/', DocumentFileUploadView.as_view(), name='document-file-upload'),
    path('files/<int:pk>/', UploadedFileDeleteView.as_view(), name='uploaded-file-delete'),
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
    path('billing/upgrade/', CreateCheckoutSessionView.as_view(), name='billing-upgrade'),
    path('billing/change-plan/', ChangePlanView.as_view(), name='billing-change-plan'),
    path('billing/portal/', CreateCustomerPortalSessionView.as_view(), name='billing-portal'),
    path('billing/cancel/', CancelSubscriptionView.as_view(), name='billing-cancel'),
    path('billing/config/', StripeConfigView.as_view(), name='billing-config'),
    path('billing/setup-intent/', CreateSetupIntentView.as_view(), name='billing-setup-intent'),
    path('billing/update-payment-method/', UpdateDefaultPaymentMethodView.as_view(), name='billing-update-payment-method'),
    path('billing/webhook/', stripe_webhook, name='stripe-webhook'),
]