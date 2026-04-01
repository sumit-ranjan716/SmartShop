"""
Views for checkout, order creation, order history, payment, and order detail.
"""
import base64
import io
from decimal import Decimal

import qrcode
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.cart.models import Cart
from apps.discounts.models import CouponCode, CouponUsage
from apps.discounts.utils import validate_coupon_for_user_and_cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from .email_utils import send_order_confirmation
from .utils import auto_add_tracking_event

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout_view(request):
    """Display checkout form and process order."""
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, 'Your cart is empty. Add some products first!')
        return redirect('products:product_list')

    items = cart.items.select_related('product').all()

    applied_discount = Decimal(request.session.get('applied_coupon_discount', '0') or '0')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.total_price
            _apply_coupon_for_order_if_any(request, cart, order)
            order.save()
            auto_add_tracking_event(order, 'pending', description='Order placed successfully.')

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

                # --- Handle Referral Conversion ---
                ref_info = request.session.get('referral_active')
                if ref_info and ref_info.get('product_id') == product.id:
                    from apps.price_tracker.models import Referral
                    try:
                        referral = Referral.objects.filter(
                            referrer_user_id=ref_info['referrer_id'],
                            product_id=product.id,
                            converted=False
                        ).order_by('-created_at').first()
                        
                        if referral:
                            referral.converted = True
                            referral.save(update_fields=['converted'])
                    except Exception:
                        pass

            if 'referral_active' in request.session:
                del request.session['referral_active']

            # For all methods we clear the cart and create the order.
            cart.items.all().delete()

            # For COD and UPI, we treat order as placed immediately and send confirmation.
            if order.payment_method in ['cod', 'upi']:
                send_order_confirmation(order)
                messages.success(
                    request,
                    f'Order #{order.order_number} placed successfully!'
                    if order.payment_method == 'cod'
                    else f'Order #{order.order_number} placed! Please complete payment via UPI.',
                )
            else:
                messages.success(
                    request,
                    f'Order #{order.order_number} created. Complete payment to confirm.',
                )

            if order.coupon:
                CouponUsage.objects.create(
                    coupon=order.coupon,
                    user=request.user,
                    order=order,
                    discount_amount=order.discount_amount,
                )
                CouponCode.objects.filter(pk=order.coupon_id).update(times_used=order.coupon.times_used + 1)
                request.session.pop('applied_coupon_code', None)
                request.session.pop('applied_coupon_discount', None)

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
        'applied_coupon_code': request.session.get('applied_coupon_code', ''),
        'applied_coupon_discount': applied_discount,
        'final_total': max(cart.total_price - applied_discount, 0),
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


def _apply_coupon_for_order_if_any(request, cart, order):
    code = request.session.get('applied_coupon_code')
    if not code:
        order.discount_amount = Decimal('0')
        return
    try:
        coupon = CouponCode.objects.get(code=code)
    except CouponCode.DoesNotExist:
        order.discount_amount = Decimal('0')
        return

    valid, result = validate_coupon_for_user_and_cart(coupon, request.user, cart)
    if not valid:
        order.discount_amount = Decimal('0')
        request.session.pop('applied_coupon_code', None)
        request.session.pop('applied_coupon_discount', None)
        return

    order.coupon = coupon
    order.discount_amount = result



@require_POST
@login_required
def create_stripe_payment_intent_view(request, order_number):
    """Create a Stripe PaymentIntent for the given order."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.is_paid:
        return JsonResponse({'error': 'Order is already paid.'}, status=400)

    amount = int(order.total * 100)
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='inr',
            metadata={'order_number': order_number},
        )
        return JsonResponse(
            {
                'client_secret': intent.client_secret,
                'public_key': settings.STRIPE_PUBLIC_KEY,
            }
        )
    except Exception as exc:  # pragma: no cover - defensive
        return JsonResponse({'error': str(exc)}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """Handle Stripe webhook events for payment status updates."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=200)

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'payment_intent.succeeded':
        order_number = data.get('metadata', {}).get('order_number')
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                order.is_paid = True
                order.payment_id = data.get('id')
                order.status = 'processing'
                order.save(update_fields=['is_paid', 'payment_id', 'status'])
                auto_add_tracking_event(order, 'processing', description='Payment received via Stripe.')
                send_order_confirmation(order)
            except Order.DoesNotExist:
                pass
    elif event_type == 'payment_intent.payment_failed':
        order_number = data.get('metadata', {}).get('order_number')
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                # Optionally log failure; here we just ensure is_paid stays False.
                order.is_paid = False
                order.save(update_fields=['is_paid'])
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)


@login_required
def generate_upi_qr_view(request, order_number):
    """Generate UPI QR code for an order and return as base64 image."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if not settings.UPI_ID:
        return JsonResponse({'error': 'UPI payments are not configured.'}, status=400)

    upi_link = (
        f"upi://pay?pa={settings.UPI_ID}&pn=SmartShop&am={order.total}&cu=INR"
        f"&tn=Order%20{order.order_number}"
    )

    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return JsonResponse({'qr_image': img_str, 'upi_link': upi_link})


@require_POST
@login_required
def confirm_upi_payment_view(request, order_number):
    """Mark order as payment claimed via UPI; admin must verify manually."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    order.status = 'processing'
    order.payment_method = 'upi'
    order.save(update_fields=['status', 'payment_method'])
    auto_add_tracking_event(order, 'processing', description='Customer marked UPI payment as completed.')

    # Notify admin for manual verification
    admin_email = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject=f'UPI payment claimed for order #{order.order_number}',
        message=(
            f'Customer {order.full_name} ({order.email}) has claimed UPI payment '
            f'for order #{order.order_number} totaling ₹{order.total}.\n\n'
            'Please verify the payment in your UPI app or bank statement.'
        ),
        from_email=admin_email,
        recipient_list=[admin_email],
        fail_silently=True,
    )

    messages.success(
        request,
        'Your order is placed! Payment will be verified within 1 hour.',
    )
    return redirect('orders:order_detail', order_number=order.order_number)


@login_required
def order_tracking_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    events = order.tracking_events.order_by('timestamp')
    progress_map = {
        'pending': 10,
        'processing': 25,
        'shipped': 50,
        'out_for_delivery': 75,
        'delivered': 100,
        'completed': 100,
        'cancelled': 0,
    }
    progress_percentage = progress_map.get(order.status, 0)
    return render(
        request,
        'orders/order_tracking.html',
        {'order': order, 'events': events, 'progress_percentage': progress_percentage},
    )


@login_required
def order_tracking_status_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    progress_map = {
        'pending': 10,
        'processing': 25,
        'shipped': 50,
        'out_for_delivery': 75,
        'delivered': 100,
        'completed': 100,
        'cancelled': 0,
    }
    events = [
        {
            'status': e.status,
            'location': e.location,
            'description': e.description,
            'timestamp': e.timestamp.isoformat(),
        }
        for e in order.tracking_events.order_by('-timestamp')
    ]
    return JsonResponse({'status': order.status, 'progress': progress_map.get(order.status, 0), 'events': events})
