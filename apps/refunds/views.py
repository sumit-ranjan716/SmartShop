from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.orders.models import Order

from .email_utils import notify_refund_created, notify_refund_status
from .forms import ExchangeRequestForm, PhotoUploadFormSet, RefundRequestForm
from .models import ExchangeRequest, RefundPhoto, RefundRequest


def is_seller(user):
    return hasattr(user, 'profile') and user.profile.is_seller


@login_required
def request_refund_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    form = RefundRequestForm(request.POST or None, user=request.user, order=order)
    photo_formset = PhotoUploadFormSet(request.POST or None, request.FILES or None, queryset=RefundPhoto.objects.none())
    if request.method == 'POST' and form.is_valid() and photo_formset.is_valid():
        rr = form.save(commit=False)
        rr.order = order
        rr.user = request.user
        rr.status = 'pending'
        rr.save()
        ctype = ContentType.objects.get_for_model(RefundRequest)
        for f in photo_formset:
            if f.cleaned_data and f.cleaned_data.get('photo'):
                RefundPhoto.objects.create(content_type=ctype, object_id=rr.pk, photo=f.cleaned_data['photo'])
        seller_email = rr.order_item.product.seller.email if rr.order_item.product and rr.order_item.product.seller else request.user.email
        notify_refund_created(request.user.email, seller_email, rr, 'refund')
        messages.success(request, 'Refund request submitted.')
        return redirect('refunds:my_requests')
    return render(request, 'refunds/request_form.html', {'form': form, 'photo_formset': photo_formset, 'type': 'refund'})


@login_required
def request_exchange_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    form = ExchangeRequestForm(request.POST or None, user=request.user, order=order)
    photo_formset = PhotoUploadFormSet(request.POST or None, request.FILES or None, queryset=RefundPhoto.objects.none())
    if request.method == 'POST' and form.is_valid() and photo_formset.is_valid():
        er = form.save(commit=False)
        er.order = order
        er.user = request.user
        er.status = 'pending'
        er.save()
        ctype = ContentType.objects.get_for_model(ExchangeRequest)
        for f in photo_formset:
            if f.cleaned_data and f.cleaned_data.get('photo'):
                RefundPhoto.objects.create(content_type=ctype, object_id=er.pk, photo=f.cleaned_data['photo'])
        seller_email = er.order_item.product.seller.email if er.order_item.product and er.order_item.product.seller else request.user.email
        notify_refund_created(request.user.email, seller_email, er, 'exchange')
        messages.success(request, 'Exchange request submitted.')
        return redirect('refunds:my_requests')
    return render(request, 'refunds/request_form.html', {'form': form, 'photo_formset': photo_formset, 'type': 'exchange'})


@login_required
def my_requests_view(request):
    refunds = RefundRequest.objects.filter(user=request.user)
    exchanges = ExchangeRequest.objects.filter(user=request.user)
    return render(request, 'refunds/my_requests.html', {'refunds': refunds, 'exchanges': exchanges})


@login_required
def request_detail_view(request, request_type, pk):
    model = RefundRequest if request_type == 'refund' else ExchangeRequest
    req = get_object_or_404(model, pk=pk, user=request.user)
    ctype = ContentType.objects.get_for_model(model)
    photos = RefundPhoto.objects.filter(content_type=ctype, object_id=req.pk)
    return render(request, 'refunds/request_detail.html', {'request_obj': req, 'request_type': request_type, 'photos': photos})


@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_refund_requests_view(request):
    refunds = RefundRequest.objects.filter(order_item__product__seller=request.user, status__in=['pending', 'seller_review'])
    exchanges = ExchangeRequest.objects.filter(order_item__product__seller=request.user, status__in=['pending', 'seller_review'])
    return render(request, 'refunds/seller_dashboard.html', {'refunds': refunds, 'exchanges': exchanges})


@require_POST
@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_approve_refund_view(request, pk):
    req = get_object_or_404(RefundRequest, pk=pk, order_item__product__seller=request.user)
    req.status = 'approved'
    req.seller_note = request.POST.get('seller_note', '')
    req.resolved_at = timezone.now()
    req.save(update_fields=['status', 'seller_note', 'resolved_at'])
    notify_refund_status(req.user.email, req, 'approved')
    messages.success(request, 'Refund approved.')
    return redirect('refunds:seller_requests')


@require_POST
@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_reject_refund_view(request, pk):
    req = get_object_or_404(RefundRequest, pk=pk, order_item__product__seller=request.user)
    req.status = 'rejected'
    req.seller_note = request.POST.get('seller_note', '')
    req.resolved_at = timezone.now()
    req.save(update_fields=['status', 'seller_note', 'resolved_at'])
    notify_refund_status(req.user.email, req, 'rejected')
    messages.success(request, 'Refund rejected.')
    return redirect('refunds:seller_requests')


@require_POST
@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_approve_exchange_view(request, pk):
    req = get_object_or_404(ExchangeRequest, pk=pk, order_item__product__seller=request.user)
    req.status = 'approved'
    req.seller_note = request.POST.get('seller_note', '')
    req.resolved_at = timezone.now()
    req.save(update_fields=['status', 'seller_note', 'resolved_at'])
    notify_refund_status(req.user.email, req, 'approved')
    messages.success(request, 'Exchange approved.')
    return redirect('refunds:seller_requests')


@require_POST
@login_required
@user_passes_test(is_seller, login_url='/users/profile/')
def seller_reject_exchange_view(request, pk):
    req = get_object_or_404(ExchangeRequest, pk=pk, order_item__product__seller=request.user)
    req.status = 'rejected'
    req.seller_note = request.POST.get('seller_note', '')
    req.resolved_at = timezone.now()
    req.save(update_fields=['status', 'seller_note', 'resolved_at'])
    notify_refund_status(req.user.email, req, 'rejected')
    messages.success(request, 'Exchange rejected.')
    return redirect('refunds:seller_requests')

