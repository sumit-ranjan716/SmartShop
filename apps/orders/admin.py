from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'status', 'total', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email']
    list_editable = ['status', 'is_paid']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number']
