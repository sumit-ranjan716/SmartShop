"""
Utility functions for sending user-related emails (verification, etc.).
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """
    Send email verification link to the given user.
    """
    try:
        profile = user.profile
        token = str(profile.email_verification_token)
        verify_url = request.build_absolute_uri(
            reverse('users:verify_email', args=[token])
        )

        context = {
            'user': user,
            'verify_url': verify_url,
            'site_name': 'SmartShop',
            'now': timezone.now(),
        }

        subject = 'SmartShop — Verify your email address'
        html_body = render_to_string('emails/email_verification.html', context)
        text_body = render_to_string('emails/email_verification.txt', context)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartshop.com')
        to_email = [user.email]

        message = EmailMultiAlternatives(subject, text_body, from_email, to_email)
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=True)

        profile.email_verification_sent_at = timezone.now()
        profile.save(update_fields=['email_verification_sent_at'])
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception('Failed to send verification email for user %s: %s', user.pk, exc)

