"""
Price Tracker Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.products.models import Product, Wishlist
from apps.users.models import Profile
from .models import PriceAlert, ProductPriceHistory
from datetime import timedelta
from django.utils import timezone


@login_required
def toggle_price_alert_view(request, product_id):
    """AJAX endpoint to toggle a price alert."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    product = get_object_or_404(Product, pk=product_id)
    target_price = request.POST.get('target_price')

    if not target_price:
        # If no target price provided, attempt to delete entirely
        PriceAlert.objects.filter(user=request.user, product=product).delete()
        return JsonResponse({'status': 'removed', 'message': 'Price alert removed.'})

    try:
        target_price = float(target_price)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid price'}, status=400)

    alert, created = PriceAlert.objects.get_or_create(
        user=request.user, 
        product=product,
        defaults={'target_price': target_price, 'is_active': True}
    )

    if not created:
        alert.target_price = target_price
        alert.is_active = True
        alert.save(update_fields=['target_price', 'is_active'])

    return JsonResponse({
        'status': 'added', 
        'message': f'Alert set for ₹{target_price:.2f}',
        'target_price': target_price
    })


@login_required
def my_alerts_view(request):
    """List all active price alerts for the user."""
    alerts = PriceAlert.objects.filter(user=request.user).select_related('product').order_by('-created_at')
    
    # Calculate price drops if any
    for alert in alerts:
        if alert.product.price <= alert.target_price and alert.is_active:
             alert.can_trigger_now = True
        else:
             alert.can_trigger_now = False

    return render(request, 'price_tracker/my_alerts.html', {'alerts': alerts})


def shared_wishlist_view(request, token):
    """View another user's public wishlist."""
    # Find profile by token
    profile = get_object_or_404(Profile, wishlist_share_token=token)
    shared_user = profile.user

    # Get their wishlist items
    wishlist_items = Wishlist.objects.filter(user=shared_user).select_related('product')
    products = [item.product for item in wishlist_items]

    return render(request, 'price_tracker/shared_wishlist.html', {
        'shared_user': shared_user,
        'products': products
    })


def price_history_api(request, product_id):
    """Returns price history data and insights for chart rendering."""
    product = get_object_or_404(Product, pk=product_id)
    days = int(request.GET.get('days', 30))
    cutoff = timezone.now() - timedelta(days=days)

    history = ProductPriceHistory.objects.filter(
        product=product, 
        recorded_at__gte=cutoff
    ).order_by('recorded_at')

    labels = []
    data = []
    
    min_price = float('inf')
    max_price = 0
    
    for h in history:
        date_str = h.recorded_at.strftime('%Y-%m-%d')
        # Only add one data point per day for simplicity if there are multiples
        if not labels or labels[-1] != date_str:
            labels.append(date_str)
            p = float(h.price)
            data.append(p)
            if p < min_price: min_price = p
            if p > max_price: max_price = p

    # Ensure current price is factored
    current_price = float(product.price)
    if current_price < min_price: min_price = current_price
    if current_price > max_price: max_price = current_price

    # Add today's price point if missing
    today_str = timezone.now().strftime('%Y-%m-%d')
    if not labels or labels[-1] != today_str:
        labels.append(today_str)
        data.append(current_price)

    insight = "Average time to buy."
    if min_price < max_price:
        range_size = max_price - min_price
        position = (current_price - min_price) / range_size
        
        if position <= 0.25:
            insight = "Great time to buy! Price is near its lowest."
        elif position >= 0.75:
            insight = "Price is high. Consider setting an alert."
    else:
        insight = "Price has been stable."

    return JsonResponse({
        'labels': labels,
        'data': data,
        'insight': insight,
        'current_price': current_price,
        'min_price': min_price if min_price != float('inf') else current_price,
        'max_price': max_price,
    })
