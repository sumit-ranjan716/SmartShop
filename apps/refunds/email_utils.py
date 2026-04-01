from django.conf import settings
from django.core.mail import send_mail


def notify_refund_created(customer_email, seller_email, request_obj, request_type='refund'):
    send_mail(
        subject=f'Your {request_type} request has been received',
        message=f'Your {request_type} request #{request_obj.pk} has been received.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=True,
    )
    send_mail(
        subject=f'New {request_type} request for your product',
        message=f'Please review request #{request_obj.pk}.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[seller_email],
        fail_silently=True,
    )


def notify_refund_status(customer_email, request_obj, status):
    send_mail(
        subject=f'Your request #{request_obj.pk} has been {status}',
        message=f'Status: {status}\nSeller note: {request_obj.seller_note}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=True,
    )

