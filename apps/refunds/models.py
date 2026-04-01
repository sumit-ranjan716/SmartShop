from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class RefundRequest(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('seller_review', 'Seller Reviewing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    REASONS = [
        ('defective', 'Defective/Damaged'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASONS)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default='pending')
    seller_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class ExchangeRequest(models.Model):
    STATUS = RefundRequest.STATUS
    REASONS = RefundRequest.REASONS

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASONS)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default='pending')
    seller_note = models.TextField(blank=True)
    exchange_for_product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    exchange_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class RefundPhoto(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    request = GenericForeignKey('content_type', 'object_id')
    photo = models.ImageField(upload_to='refund_photos/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

