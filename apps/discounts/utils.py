from decimal import Decimal

from django.utils import timezone

from apps.cart.models import Cart

from .models import CouponCode, CouponUsage


def coupon_scope_matches_cart(coupon, cart):
    items = cart.items.select_related('product', 'product__category', 'product__seller').all()
    if not items:
        return False

    if coupon.applies_to == 'all':
        return True
    if coupon.applies_to == 'product':
        return any(item.product_id == coupon.product_id for item in items)
    if coupon.applies_to == 'category':
        return any(item.product.category_id == coupon.category_id for item in items)
    if coupon.applies_to == 'seller':
        return any(item.product.seller_id == coupon.seller_id for item in items)
    return False


def calculate_coupon_discount(coupon, subtotal):
    subtotal = Decimal(subtotal)
    discount = Decimal('0')
    if coupon.discount_type == 'percentage':
        discount = (subtotal * coupon.value) / Decimal('100')
        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = coupon.value
    return max(Decimal('0'), min(discount, subtotal))


def validate_coupon_for_user_and_cart(coupon, user, cart):
    if not coupon.is_active:
        return False, 'Coupon is inactive.'
    now = timezone.now()
    if now < coupon.start_date or now > coupon.end_date:
        return False, 'Coupon is expired or not yet active.'
    if coupon.times_used >= coupon.usage_limit:
        return False, 'Coupon usage limit reached.'

    subtotal = cart.total_price
    if subtotal < coupon.min_order_amount:
        return False, f'Minimum order amount is ₹{coupon.min_order_amount}.'

    if not coupon_scope_matches_cart(coupon, cart):
        return False, 'Coupon is not applicable to products in your cart.'

    if user.is_authenticated:
        used_count = CouponUsage.objects.filter(coupon=coupon, user=user).count()
        if used_count >= coupon.usage_per_user:
            return False, 'You have already used this coupon the maximum allowed times.'

    discount = calculate_coupon_discount(coupon, subtotal)
    if discount <= 0:
        return False, 'Coupon does not provide a valid discount for this cart.'
    return True, discount


def get_cart_for_request(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).first()
    if not request.session.session_key:
        return None
    return Cart.objects.filter(session_key=request.session.session_key).first()

