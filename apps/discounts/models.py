from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.orders.models import Order
from apps.products.models import Category, Product


class Discount(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage %'),
        ('flat', 'Flat Amount ₹'),
    ]

    product = models.ForeignKey(Product, null=True, blank=True, related_name='discounts', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='discounts', on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.product.name if self.product else (self.category.name if self.category else 'Global')
        return f'{target} - {self.value}'

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def calculate_discounted_price(self, original_price):
        original = Decimal(original_price)
        discount_amount = Decimal('0')

        if self.discount_type == 'percentage':
            discount_amount = (original * self.value) / Decimal('100')
            if self.max_discount_amount is not None:
                discount_amount = min(discount_amount, self.max_discount_amount)
        elif self.discount_type == 'flat':
            discount_amount = self.value

        discount_amount = max(Decimal('0'), min(discount_amount, original))
        return max(Decimal('0'), original - discount_amount)


class CouponCode(models.Model):
    APPLIES_TO = [
        ('all', 'All Products'),
        ('category', 'Specific Category'),
        ('product', 'Specific Product'),
        ('seller', 'Seller Products'),
    ]

    code = models.CharField(max_length=50, unique=True, db_index=True)
    seller = models.ForeignKey(User, related_name='coupons', on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=Discount.DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    applies_to = models.CharField(max_length=20, choices=APPLIES_TO, default='all')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    usage_limit = models.PositiveIntegerField(default=100)
    usage_per_user = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date and self.times_used < self.usage_limit


class CouponUsage(models.Model):
    coupon = models.ForeignKey(CouponCode, related_name='usages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    used_at = models.DateTimeField(auto_now_add=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-used_at']

    def __str__(self):
        return f'{self.coupon.code} used by {self.user.username}'

