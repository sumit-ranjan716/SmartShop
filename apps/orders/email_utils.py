"""
Utility functions for sending order-related emails.
"""
from collections import defaultdict

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


def _get_base_context(order):
    return {
        "order": order,
        "items": order.items.select_related("product").all(),
        "site_name": "SmartShop",
        "currency_symbol": "₹",
        "now": timezone.now(),
        "tracking_url": f"{settings.SITE_URL}/orders/{order.order_number}/tracking/",
    }


def send_order_confirmation(order):
    """
    Send order confirmation email to customer and per-seller summaries.
    Any failure is logged but does not block order completion.
    """
    try:
        context = _get_base_context(order)

        # Customer email
        subject = f"SmartShop — Order Confirmation #{order.order_number}"
        html_body = render_to_string("emails/order_confirmation.html", context)
        text_body = render_to_string("emails/order_confirmation.txt", context)

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@smartshop.com")
        to_email = [order.email]

        message = EmailMultiAlternatives(subject, text_body, from_email, to_email)
        message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=True)

        # Seller notifications: group items by seller
        seller_items = defaultdict(list)
        for item in context["items"]:
            seller = getattr(item.product, "seller", None)
            if seller and seller.email:
                seller_items[seller].append(item)

        for seller, items in seller_items.items():
            seller_context = {
                **context,
                "items": items,
                "seller": seller,
                "is_seller_notification": True,
            }
            seller_subject = f"SmartShop — New Order #{order.order_number} for your products"
            seller_html = render_to_string("emails/order_confirmation.html", seller_context)
            seller_text = render_to_string("emails/order_confirmation.txt", seller_context)

            seller_message = EmailMultiAlternatives(
                seller_subject,
                seller_text,
                from_email,
                [seller.email],
            )
            seller_message.attach_alternative(seller_html, "text/html")
            seller_message.send(fail_silently=True)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to send order confirmation emails for order %s: %s", order.pk, exc)

