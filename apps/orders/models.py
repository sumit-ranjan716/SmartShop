"""
Order and OrderItem models for the checkout/order flow.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.products.models import Product


class Order(models.Model):
    """Represents a customer order."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('stripe', 'Credit/Debit Card (Stripe)'),
        ('upi', 'UPI / QR Code'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey('discounts.CouponCode', null=True, blank=True, on_delete=models.SET_NULL)
    estimated_delivery = models.DateField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)

    # Shipping details
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.order_number}'

    def save(self, *args, **kwargs):
        """Auto-generate order number if not set."""
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:12].upper()
        if not self.estimated_delivery:
            self.estimated_delivery = (timezone.now() + timedelta(days=5)).date()
        self.total = max(self.subtotal - self.discount_amount, 0)
        super().save(*args, **kwargs)

    @property
    def can_request_refund(self):
        if self.status not in ['delivered', 'completed']:
            return False
        return timezone.now() <= self.created_at + timedelta(days=7)


class OrderItem(models.Model):
    """Individual item within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=300)  # Snapshot of name at purchase time
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity}x {self.product_name}'

    @property
    def subtotal(self):
        return self.price * self.quantity


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, related_name='tracking_events', on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.order.order_number} - {self.status}'
