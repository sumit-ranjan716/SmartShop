from django.contrib import admin

from .models import CouponCode, CouponUsage, Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'product', 'category', 'discount_type', 'value', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'seller', 'discount_type']
    search_fields = ['label', 'product__name', 'category__name', 'seller__username']


@admin.register(CouponCode)
class CouponCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'seller', 'discount_type', 'value', 'applies_to', 'times_used', 'usage_limit', 'is_active']
    list_filter = ['is_active', 'seller', 'discount_type', 'applies_to']
    search_fields = ['code', 'seller__username']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'discount_amount', 'used_at']
    list_filter = ['coupon', 'used_at']
    search_fields = ['coupon__code', 'user__username', 'order__order_number']

