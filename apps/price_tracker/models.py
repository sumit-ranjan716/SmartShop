from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class ProductPriceHistory(models.Model):
    """Tracks historical prices for a product over time."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['recorded_at']

    def __str__(self):
        return f'{self.product.name} - ₹{self.price} at {self.recorded_at.strftime("%Y-%m-%d %H:%M")}'


class PriceAlert(models.Model):
    """User-defined alert to trigger when a product price drops."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_alerts')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.name} at ₹{self.target_price}'


class Referral(models.Model):
    """Tracks social sharing referrals."""
    referrer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='referrals')
    visitor_ip = models.GenericIPAddressField(blank=True, null=True)
    converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.referrer_user.username} shared {self.product.name} ({self.converted})'
