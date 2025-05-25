from django.urls import path

from users.views.activity import ActivityLogViewForCompany
from .views import (
    UserListView, UserDetailView,
    RoleListView, RoleDetailView,
    PermissionListView, PermissionDetailView,
    ActivityLogView
)
from .views.auth import (
    LoginView, VerifyOTPView, ResendOTPView, 
    RefreshTokenView, VerifyTokenView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/<uuid:id>/', RoleDetailView.as_view(), name='role-detail'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('permissions/<uuid:id>/', PermissionDetailView.as_view(), name='permission-detail'),
    path('activity-logs/', ActivityLogView.as_view(), name='activity-log-list'),
    path('activity-logs/company/<uuid:company_id>/', ActivityLogViewForCompany.as_view(), name='activity-log-list-for-company'),
    
    # Auth URLs
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='auth-verify-otp'),
    path('auth/resend-otp/', ResendOTPView.as_view(), name='auth-resend-otp'),
    path('auth/refresh-token/', RefreshTokenView.as_view(), name='auth-refresh-token'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='auth-verify-token'),
    
    # Password Reset URLs
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
] 
