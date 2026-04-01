from django.contrib import admin
from .models import Order, OrderItem, OrderTracking
from .utils import auto_add_tracking_event
from apps.delivery.admin import DeliveryAssignmentInline


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    fields = ['status', 'location', 'description', 'timestamp', 'updated_by']
    readonly_fields = ['timestamp']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'status', 'total', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email']
    list_editable = ['status', 'is_paid']
    inlines = [OrderItemInline, OrderTrackingInline, DeliveryAssignmentInline]
    readonly_fields = ['order_number']
    actions = ['mark_paid_upi_verified']

    @admin.action(description='Mark as Paid (UPI verified)')
    def mark_paid_upi_verified(self, request, queryset):
        queryset.update(is_paid=True, status='processing', payment_method='upi')

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = Order.objects.get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if not change or old_status != obj.status:
            auto_add_tracking_event(
                obj,
                obj.status,
                description='Order status updated',
                updated_by=request.user,
            )
