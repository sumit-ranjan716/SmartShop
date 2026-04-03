from django.contrib import admin
from .models import Profile, RecoveryCode


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_verified', 'is_seller', 'is_delivery_person', 'city', 'two_factor_enabled']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_filter = ['email_verified', 'is_seller', 'is_delivery_person', 'two_factor_enabled']
    actions = ['mark_email_verified', 'resend_verification']

    @admin.action(description='Manually verify selected users')
    def mark_email_verified(self, request, queryset):
        queryset.update(email_verified=True)

    @admin.action(description='Resend verification to selected users')
    def resend_verification(self, request, queryset):
        from .email_utils import send_verification_email

        for profile in queryset.select_related('user'):
            if not profile.email_verified and profile.user.email:
                class DummyRequest:
                    def __init__(self, scheme, host):
                        self.scheme = scheme
                        self._host = host

                    def build_absolute_uri(self, location):
                        return f'{self.scheme}://{self._host}{location}'

                dummy_request = DummyRequest('https', request.get_host())
                send_verification_email(profile.user, dummy_request)


@admin.register(RecoveryCode)
class RecoveryCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'used', 'created_at']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username', 'user__email']
