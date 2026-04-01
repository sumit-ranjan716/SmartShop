"""URL patterns for the users app."""
from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('become-seller/', views.become_seller_view, name='become_seller'),
    path('become-delivery-person/', views.become_delivery_person_view, name='become_delivery_person'),
    path('registration-pending/', views.registration_pending_view, name='registration_pending'),
    path('verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    path('2fa/setup/', views.two_factor_setup_view, name='2fa_setup'),
    path('2fa/recovery-codes/', views.two_factor_recovery_codes_view, name='2fa_recovery_codes'),
    path('2fa/verify/', views.two_factor_verify_view, name='2fa_verify'),
    path('2fa/disable/', views.two_factor_disable_view, name='2fa_disable'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='emails/password_reset_email.txt',
            html_email_template_name='emails/password_reset_email.html',
            subject_template_name='emails/password_reset_subject.txt',
            success_url=reverse_lazy('users:password_reset_done'),
            form_class=views.RateLimitedPasswordResetForm,
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
