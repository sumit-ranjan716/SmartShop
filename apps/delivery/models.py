"""
DeliveryAssignment model — tracks the assignment and lifecycle of a delivery.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.orders.models import Order


class DeliveryAssignment(models.Model):
    """Tracks the delivery lifecycle for an order."""
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    CANCELLATION_REASONS = [
        ('customer_not_available', 'Customer Not Available'),
        ('wrong_address', 'Wrong Address'),
        ('customer_refused', 'Customer Refused'),
        ('item_damaged', 'Item Damaged'),
        ('other', 'Other'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_assignment')
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=30, blank=True, choices=CANCELLATION_REASONS)
    cancellation_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='cancelled_deliveries'
    )
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'Delivery #{self.pk} — Order {self.order.order_number} ({self.status})'
