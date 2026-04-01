"""
Views for user registration, login, logout, profile management, password reset,
and email verification.
"""
from datetime import timedelta

from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordResetForm
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_POST
from django import forms

from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile, RecoveryCode
from .email_utils import send_verification_email

import qrcode
import io
import base64
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.models import User


class RateLimitedPasswordResetForm(PasswordResetForm):
    """Password reset form with simple per-email rate limiting using cache."""

    RATE_LIMIT = 3
    WINDOW_SECONDS = 3600

    def clean_email(self):
        email = super().clean_email()
        normalized_email = email.strip().lower()
        cache_key = f"password_reset_requests:{normalized_email}"
        count = cache.get(cache_key, 0)

        if count >= self.RATE_LIMIT:
            raise forms.ValidationError(
                "Too many requests. Please try again in 1 hour."
            )

        cache.set(cache_key, count + 1, self.WINDOW_SECONDS)
        return email


def register_view(request):
    """Handle user registration with email verification step."""
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user, request)
            messages.success(
                request,
                f"Welcome! We've sent a verification email to {user.email}. "
                "Please verify before logging in.",
            )
            request.session['pending_verification_email'] = user.email
            return redirect('users:registration_pending')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view with Bootstrap-styled form."""
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if hasattr(user, 'profile') and not user.profile.email_verified:
            resend_url = ''
            try:
                from django.urls import reverse
                resend_url = reverse('users:resend_verification')
            except Exception:
                pass
            error_html = "Please verify your email first."
            if resend_url:
                error_html += f' <a href="{resend_url}?email={user.email}">Resend verification email</a>'
            messages.error(self.request, error_html)
            return redirect('users:login')

        if hasattr(user, 'profile') and user.profile.two_factor_enabled:
            self.request.session['_pending_2fa_user'] = user.pk
            return redirect('users:2fa_verify')

        login(self.request, user)
        messages.success(self.request, f'Welcome back, {user.username}!')
        return redirect(self.get_success_url())


def logout_view(request):
    """Logout the user and redirect to home."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('products:product_list')


@login_required
def profile_view(request):
    """Display and update user profile."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/profile.html', context)


@login_required
def become_seller_view(request):
    """Upgrade user to seller account."""
    if request.method == 'POST':
        profile = request.user.profile
        if not profile.is_seller:
            profile.is_seller = True
            profile.save()
            messages.success(request, 'Congratulations! You are now a Seller.')
        return redirect('products:seller_dashboard')
    return redirect('users:profile')


@login_required
def become_delivery_person_view(request):
    """Upgrade user to delivery partner."""
    if request.method == 'POST':
        profile = request.user.profile
        if not profile.is_delivery_person and not profile.is_seller:
            vehicle_type = request.POST.get('vehicle_type', '')
            service_areas = request.POST.get('service_areas', '')
            profile.is_delivery_person = True
            profile.vehicle_type = vehicle_type
            profile.service_areas = service_areas
            profile.save()
            messages.success(request, 'Congratulations! You are now a Delivery Partner.')
            return redirect('delivery:delivery_home')
    return redirect('users:profile')



def registration_pending_view(request):
    """Show info after registration, prompting user to verify email."""
    email = request.session.get('pending_verification_email', 'your email')
    verification_token = None
    if settings.DEBUG and email != 'your email':
        profile = Profile.objects.filter(user__email__iexact=email).first()
        if profile:
            verification_token = profile.email_verification_token

    return render(request, 'users/registration_pending.html', {
        'email': email,
        'verification_token': verification_token,
        'debug': settings.DEBUG
    })


def verify_email_view(request, token):
    """Handle email verification link."""
    try:
        profile = get_object_or_404(Profile, email_verification_token=token)
    except (ValueError, TypeError):
        return render(request, 'users/verify_error.html', status=400)

    user = profile.user

    if profile.email_verified:
        messages.info(request, 'Your email is already verified. Please log in.')
        return redirect('users:login')

    # Optional: enforce 24h expiry on verification links
    if profile.email_verification_sent_at:
        if timezone.now() - profile.email_verification_sent_at > timedelta(hours=24):
            return render(request, 'users/verify_error.html', status=400)

    profile.email_verified = True
    profile.save(update_fields=['email_verified'])

    login(request, user)
    messages.success(request, 'Email verified! Welcome to SmartShop!')
    return redirect('products:product_list')


@require_POST
def resend_verification_view(request):
    """Resend verification email with simple rate limiting (5 minutes per email)."""
    email = request.POST.get('email') or request.GET.get('email')
    if not email:
        messages.error(request, 'Please provide an email address.')
        return redirect('users:login')

    email = email.strip().lower()
    cache_key = f"resend_verification:{email}"
    if cache.get(cache_key):
        messages.error(request, 'Verification email was recently sent. Please try again in a few minutes.')
        return redirect('users:login')

    try:
        profile = Profile.objects.select_related('user').get(user__email__iexact=email)
    except Profile.DoesNotExist:
        messages.error(request, 'No account found with that email address.')
        return redirect('users:login')

    if profile.email_verified:
        messages.info(request, 'This email is already verified. You can log in.')
        return redirect('users:login')

    send_verification_email(profile.user, request)
    cache.set(cache_key, True, 300)  # 5 minutes
    messages.success(request, f'We have resent the verification email to {email}.')
    request.session['pending_verification_email'] = email
    return redirect('users:registration_pending')


@login_required
def two_factor_setup_view(request):
    """Setup 2FA with QR Code and recovery codes."""
    if request.user.profile.two_factor_enabled:
        messages.info(request, "2FA is already enabled.")
        return redirect('users:profile')

    device, created = TOTPDevice.objects.get_or_create(user=request.user, name="default")
    
    if request.method == 'POST':
        token = request.POST.get('token', '')
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            profile = request.user.profile
            profile.two_factor_enabled = True
            profile.save(update_fields=['two_factor_enabled'])
            
            # Generate recovery codes
            codes = RecoveryCode.generate_codes(request.user)
            request.session['temp_recovery_codes'] = codes

            messages.success(request, 'Two-Factor Authentication successfully enabled!')
            return redirect('users:2fa_recovery_codes')
        else:
            messages.error(request, 'Invalid token. Please try again.')

    # Generate QR Code
    url = device.config_url
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render(request, 'users/2fa_setup.html', {'qr_code': qr_b64, 'secret': device.key})


@login_required
def two_factor_recovery_codes_view(request):
    codes = request.session.pop('temp_recovery_codes', None)
    if not codes:
        return redirect('users:profile')
    return render(request, 'users/2fa_recovery_codes.html', {'codes': codes})


def two_factor_verify_view(request):
    """Verify 2FA token during login."""
    pending_user_id = request.session.get('_pending_2fa_user')
    if not pending_user_id:
        return redirect('users:login')

    try:
        user = User.objects.get(pk=pending_user_id)
    except User.DoesNotExist:
        return redirect('users:login')

    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        # Check TOTP
        if device and device.verify_token(token):
            del request.session['_pending_2fa_user']
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('products:product_list')
        
        # Check Recovery Code
        else:
            hashed_token = RecoveryCode.hash_code(token)
            recovery_code = RecoveryCode.objects.filter(user=user, code_hash=hashed_token, used=False).first()
            if recovery_code:
                recovery_code.used = True
                recovery_code.save(update_fields=['used'])
                del request.session['_pending_2fa_user']
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}! (Logged in via recovery code)')
                return redirect('products:product_list')
            
            messages.error(request, 'Invalid authentication code.')

    return render(request, 'users/2fa_verify.html')


@login_required
def two_factor_disable_view(request):
    if not request.user.profile.two_factor_enabled:
        return redirect('users:profile')
        
    if request.method == 'POST':
        TOTPDevice.objects.filter(user=request.user).delete()
        RecoveryCode.objects.filter(user=request.user).delete()
        profile = request.user.profile
        profile.two_factor_enabled = False
        profile.save(update_fields=['two_factor_enabled'])
        messages.success(request, 'Two-Factor Authentication has been disabled.')
        return redirect('users:profile')

    return render(request, 'users/2fa_disable.html')
