"""
Views for cart operations: add, remove, update, display.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .models import Cart, CartItem


def _get_or_create_cart(request):
    """Get or create cart for the current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart

    # Guest cart via session
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Display the shopping cart."""
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart_view(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    # Don't exceed available stock
    if cart_item.quantity > product.stock:
        cart_item.quantity = product.stock
        messages.warning(request, f'Only {product.stock} units of "{product.name}" available.')

    cart_item.save()
    messages.success(request, f'"{product.name}" added to your cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart'))


@require_POST
def update_cart_view(request, item_id):
    """Update quantity of a cart item."""
    cart_item = get_object_or_404(CartItem, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    else:
        if quantity > cart_item.product.stock:
            quantity = cart_item.product.stock
            messages.warning(request, f'Only {cart_item.product.stock} units available.')
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')

    return redirect('cart:cart')


def remove_from_cart_view(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, pk=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f'"{product_name}" removed from your cart.')
    return redirect('cart:cart')


def clear_cart_view(request):
    """Clear all items from the cart."""
    cart = _get_or_create_cart(request)
    cart.items.all().delete()
    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart:cart')
