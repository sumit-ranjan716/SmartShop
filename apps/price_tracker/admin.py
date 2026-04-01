from django.contrib import admin
from .models import ProductPriceHistory, PriceAlert, Referral


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'price', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['product__name']
    readonly_fields = ['recorded_at']


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'target_price', 'is_active', 'created_at', 'triggered_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['referrer_user', 'product', 'visitor_ip', 'converted', 'created_at']
    list_filter = ['converted', 'created_at']
    search_fields = ['referrer_user__username', 'product__name', 'visitor_ip']
    readonly_fields = ['created_at']
