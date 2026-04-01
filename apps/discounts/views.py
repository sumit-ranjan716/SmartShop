import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CouponCodeForm, DiscountForm
from .models import CouponCode, CouponUsage, Discount
from .utils import get_cart_for_request, validate_coupon_for_user_and_cart


def is_seller(user):
    return hasattr(user, 'profile') and user.profile.is_seller


def _random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def discount_dashboard_view(request):
    discounts = Discount.objects.filter(seller=request.user).select_related('product', 'category')
    coupons = CouponCode.objects.filter(seller=request.user)
    usage_stats = CouponUsage.objects.filter(coupon__seller=request.user).aggregate(
        total_discount=Sum('discount_amount')
    )
    context = {
        'discounts': discounts,
        'coupons': coupons,
        'total_discount_given': usage_stats['total_discount'] or 0,
    }
    return render(request, 'discounts/dashboard.html', context)


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def create_discount_view(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.seller = request.user
            form.save()
            messages.success(request, 'Discount created successfully.')
            return redirect('discounts:dashboard')
    else:
        form = DiscountForm()
    return render(request, 'discounts/discount_form.html', {'form': form, 'title': 'Create Discount'})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def edit_discount_view(request, pk):
    discount = get_object_or_404(Discount, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount updated.')
            return redirect('discounts:dashboard')
    else:
        form = DiscountForm(instance=discount)
    return render(request, 'discounts/discount_form.html', {'form': form, 'title': 'Edit Discount'})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def delete_discount_view(request, pk):
    discount = get_object_or_404(Discount, pk=pk, seller=request.user)
    if request.method == 'POST':
        discount.delete()
        messages.success(request, 'Discount deleted.')
    return redirect('discounts:dashboard')


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def create_coupon_view(request):
    if request.method == 'POST':
        form = CouponCodeForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.seller = request.user
            if not coupon.code:
                coupon.code = _random_code()
            coupon.code = coupon.code.upper()
            coupon.save()
            messages.success(request, f'Coupon {coupon.code} created.')
            return redirect('discounts:dashboard')
    else:
        form = CouponCodeForm(initial={'code': _random_code()})
    return render(request, 'discounts/coupon_form.html', {'form': form, 'title': 'Create Coupon'})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def edit_coupon_view(request, pk):
    coupon = get_object_or_404(CouponCode, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = CouponCodeForm(request.POST, instance=coupon)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.code = coupon.code.upper()
            coupon.save()
            messages.success(request, 'Coupon updated.')
            return redirect('discounts:dashboard')
    else:
        form = CouponCodeForm(instance=coupon)
    return render(request, 'discounts/coupon_form.html', {'form': form, 'title': 'Edit Coupon'})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def delete_coupon_view(request, pk):
    coupon = get_object_or_404(CouponCode, pk=pk, seller=request.user)
    if request.method == 'POST':
        coupon.delete()
        messages.success(request, 'Coupon deleted.')
    return redirect('discounts:dashboard')


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def coupon_stats_view(request, pk):
    coupon = get_object_or_404(CouponCode, pk=pk, seller=request.user)
    usages = coupon.usages.select_related('user', 'order')
    stats = usages.aggregate(total_discount=Sum('discount_amount'))
    context = {'coupon': coupon, 'usages': usages, 'total_discount': stats['total_discount'] or 0}
    return render(request, 'discounts/coupon_stats.html', context)


@require_POST
def apply_coupon_view(request):
    code = (request.POST.get('code') or '').strip().upper()
    if not code:
        return JsonResponse({'valid': False, 'message': 'Please enter a coupon code.'}, status=400)

    cart = get_cart_for_request(request)
    if not cart:
        return JsonResponse({'valid': False, 'message': 'Cart not found.'}, status=400)

    try:
        coupon = CouponCode.objects.get(code=code)
    except CouponCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid coupon code.'}, status=400)

    valid, result = validate_coupon_for_user_and_cart(coupon, request.user, cart)
    if not valid:
        return JsonResponse({'valid': False, 'message': str(result)}, status=400)

    discount = result
    request.session['applied_coupon_code'] = coupon.code
    request.session['applied_coupon_discount'] = str(discount)
    request.session.modified = True

    return JsonResponse({
        'valid': True,
        'discount_amount': float(discount),
        'message': f'₹{discount} discount applied!',
    })


@require_POST
def remove_coupon_view(request):
    request.session.pop('applied_coupon_code', None)
    request.session.pop('applied_coupon_discount', None)
    request.session.modified = True
    return JsonResponse({'removed': True})

