"""
Views for checkout, order creation, order history, and order detail.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from apps.cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout_view(request):
    """Display checkout form and process order."""
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('products:product_list')

    items = cart.items.select_related('product').all()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.total_price
            order.total = cart.total_price  # Add shipping/tax logic here if needed
            order.save()

            # Create order items from cart
            for cart_item in items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )
                # Decrease stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Clear the cart
            cart.items.all().delete()

            # Send confirmation email (console in development)
            try:
                send_mail(
                    subject=f'Order Confirmation - #{order.order_number}',
                    message=(
                        f'Hi {order.full_name},\n\n'
                        f'Thank you for your order #{order.order_number}!\n'
                        f'Total: ₹{order.total}\n\n'
                        f'We will notify you when your order ships.\n\n'
                        f'Best regards,\nSmart E-Commerce'
                    ),
                    from_email='noreply@smartecommerce.com',
                    recipient_list=[order.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Don't block order on email failure

            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('orders:order_detail', order_number=order.order_number)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with profile data
        initial = {
            'full_name': f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username,
            'email': request.user.email,
            'phone': request.user.profile.phone,
            'address': request.user.profile.address,
            'city': request.user.profile.city,
            'state': request.user.profile.state,
            'zipcode': request.user.profile.zipcode,
        }
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_history_view(request):
    """Display user's order history."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    """Display details of a specific order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    items = order.items.all()
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'orders/order_detail.html', context)
