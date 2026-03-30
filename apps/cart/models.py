"""
Cart and CartItem models for session-based and user-based carts.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):
    """Shopping cart — linked to a user or a session key for guests."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f'Cart of {self.user.username}'
        return f'Guest Cart ({self.session_key})'

    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Count total number of items in cart."""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual item inside a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

    @property
    def subtotal(self):
        return self.product.price * self.quantity
