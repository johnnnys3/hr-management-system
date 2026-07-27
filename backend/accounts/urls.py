from django.urls import path

from .views import (
    CsrfBootstrapView,
    EmailVerificationConfirmView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
    SecondFactorEnrollView,
    SecondFactorRecoveryRequestCreateView,
    SecondFactorRecoveryRequestDecideView,
)

urlpatterns = [
    path('auth/csrf/', CsrfBootstrapView.as_view(), name='auth-csrf'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('auth/email/confirm/', EmailVerificationConfirmView.as_view(), name='auth-email-confirm'),
    path('auth/phone/', PhoneVerificationRequestView.as_view(), name='auth-phone'),
    path('auth/phone/confirm/', PhoneVerificationConfirmView.as_view(), name='auth-phone-confirm'),
    path('auth/second-factor/', SecondFactorEnrollView.as_view(), name='auth-second-factor'),
    path('auth/second-factor/recovery-requests/', SecondFactorRecoveryRequestCreateView.as_view(),
         name='auth-second-factor-recovery-requests'),
    path('auth/second-factor/recovery-requests/<int:pk>/decide/', SecondFactorRecoveryRequestDecideView.as_view(),
         name='auth-second-factor-recovery-request-decide'),
]
