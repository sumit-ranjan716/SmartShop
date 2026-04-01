"""
Utility functions for sending price drop alerts.
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging


logger = logging.getLogger(__name__)


def send_price_drop_alert(alert, current_price):
    """
    Send email alert user about price drop on a product.
    """
    try:
        context = {
            'user': alert.user,
            'product': alert.product,
            'target_price': alert.target_price,
            'current_price': current_price,
            'site_name': 'SmartShop',
            'product_url': f"{settings.SITE_URL}{alert.product.get_absolute_url()}",
        }

        subject = f'Price Drop Alert: {alert.product.name} is now ₹{current_price}!'
        html_body = render_to_string('emails/price_drop_alert.html', context)
        text_body = render_to_string('emails/price_drop_alert.txt', context)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartshop.com')
        to_email = [alert.user.email]

        message = EmailMultiAlternatives(subject, text_body, from_email, to_email)
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=True)

    except Exception as exc:  # pragma: no cover
        logger.exception('Failed to send price drop email for alert %s: %s', alert.pk, exc)
