"""
User Profile model — extends the built-in Django User model.
"""
import hashlib
import secrets
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    """Extended user profile with additional fields."""
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('van', 'Van'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_seller = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Delivery person fields
    is_delivery_person = models.BooleanField(default=False)
    vehicle_type = models.CharField(max_length=50, blank=True, choices=VEHICLE_CHOICES)
    service_areas = models.TextField(blank=True, help_text='Comma-separated city names')
    is_available = models.BooleanField(default=True)
    total_deliveries = models.PositiveIntegerField(default=0)

    # 2FA
    two_factor_enabled = models.BooleanField(default=False)

    # Shared wishlist
    wishlist_share_token = models.UUIDField(default=uuid.uuid4, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_email_sent(self):
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_sent_at'])

    def get_service_areas_list(self):
        """Return list of service area cities (lowercase, stripped)."""
        if not self.service_areas:
            return []
        return [a.strip().lower() for a in self.service_areas.split(',') if a.strip()]

    def __str__(self):
        return f'{self.user.username} Profile'

    class Meta:
        ordering = ['-created_at']


class RecoveryCode(models.Model):
    """One-time recovery codes for 2FA bypass."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recovery_codes')
    code_hash = models.CharField(max_length=128)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recovery code for {self.user.username} (used={self.used})'

    @staticmethod
    def hash_code(code):
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def generate_codes(user, count=8):
        """Generate recovery codes, store hashed, return plain codes."""
        # Delete old codes
        RecoveryCode.objects.filter(user=user).delete()
        plain_codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8 char hex
            RecoveryCode.objects.create(
                user=user,
                code_hash=RecoveryCode.hash_code(code),
            )
            plain_codes.append(code)
        return plain_codes
