from .models import OrderTracking


def auto_add_tracking_event(order, status, location='', description='', updated_by=None):
    if not description:
        description = f'Order moved to {status.replace("_", " ").title()}.'
    return OrderTracking.objects.create(
        order=order,
        status=status,
        location=location,
        description=description,
        updated_by=updated_by,
    )

