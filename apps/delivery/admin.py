from django.contrib import admin
from .models import DeliveryAssignment


@admin.register(DeliveryAssignment)
class DeliveryAssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'delivery_person', 'status', 'assigned_at', 'delivered_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['order__order_number', 'delivery_person__username']
    raw_id_fields = ['order', 'delivery_person', 'cancellation_by']
    readonly_fields = ['assigned_at']


class DeliveryAssignmentInline(admin.StackedInline):
    """Inline for showing delivery assignment on OrderAdmin."""
    model = DeliveryAssignment
    extra = 0
    readonly_fields = ['assigned_at', 'picked_up_at', 'delivered_at', 'cancelled_at']
    fields = [
        'delivery_person', 'status', 'assigned_at', 'picked_up_at',
        'delivered_at', 'cancelled_at', 'cancellation_reason', 'notes',
    ]
