from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import ExchangeRequest, RefundPhoto, RefundRequest


class RefundPhotoInline(GenericTabularInline):
    model = RefundPhoto
    extra = 0


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'user', 'status', 'reason', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    list_editable = ['status']
    inlines = [RefundPhotoInline]


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'user', 'status', 'reason', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    list_editable = ['status']
    inlines = [RefundPhotoInline]


@admin.register(RefundPhoto)
class RefundPhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_type', 'object_id', 'uploaded_at']

