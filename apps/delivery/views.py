"""
Views for the delivery app — admin/seller assignment and delivery person portal.
"""
from django.db.models import Sum, Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.orders.models import Order
from apps.orders.utils import auto_add_tracking_event
from .models import DeliveryAssignment
from .forms import AssignDeliveryForm, CancelDeliveryForm
from .decorators import delivery_person_required


# ─────────────────────────────────────────────
# ADMIN / SELLER VIEWS
# ─────────────────────────────────────────────

@login_required
def assign_delivery_view(request, order_number):
    """Assign a delivery person to an order."""
    order = get_object_or_404(Order, order_number=order_number)

    # Only staff or the seller of the order's products can assign
    if not request.user.is_staff and not request.user.profile.is_seller:
        messages.error(request, 'You are not authorised to assign deliveries.')
        return redirect('orders:order_detail', order_number=order_number)

    if hasattr(order, 'delivery_assignment'):
        messages.warning(request, 'This order already has a delivery person assigned.')
        return redirect('delivery:admin_dashboard')

    # Filter available delivery persons by city match
    order_city = order.city.strip().lower()
    available_dp = User.objects.filter(
        profile__is_delivery_person=True,
        profile__is_available=True,
    )
    # Further filter by service areas containing the order city
    if order_city:
        matching_ids = []
        for dp in available_dp:
            if order_city in dp.profile.get_service_areas_list():
                matching_ids.append(dp.pk)
        if matching_ids:
            available_dp = available_dp.filter(pk__in=matching_ids)
        # If no match, show all available delivery persons

    form = AssignDeliveryForm(request.POST or None, queryset=available_dp)

    if request.method == 'POST' and form.is_valid():
        dp_user = form.cleaned_data['delivery_person']
        DeliveryAssignment.objects.create(
            order=order,
            delivery_person=dp_user,
        )
        order.status = 'processing'
        order.save(update_fields=['status'])
        auto_add_tracking_event(
            order, 'processing',
            description=f'Delivery assigned to {dp_user.get_full_name() or dp_user.username}.',
            updated_by=request.user,
        )
        messages.success(request, f'Delivery assigned to {dp_user.username} for order #{order.order_number}.')
        return redirect('delivery:admin_dashboard')

    return render(request, 'delivery/assign_delivery.html', {
        'order': order,
        'form': form,
    })


@login_required
def admin_delivery_dashboard_view(request):
    """Dashboard for admins/sellers to see all delivery assignments."""
    if not request.user.is_staff and not request.user.profile.is_seller:
        messages.error(request, 'Access denied.')
        return redirect('products:product_list')

    assignments = DeliveryAssignment.objects.select_related(
        'order', 'delivery_person', 'delivery_person__profile'
    ).all()

    # Filters
    status_filter = request.GET.get('status', '')
    dp_filter = request.GET.get('dp', '')
    date_filter = request.GET.get('date', '')

    if status_filter:
        assignments = assignments.filter(status=status_filter)
    if dp_filter:
        assignments = assignments.filter(delivery_person__username__icontains=dp_filter)
    if date_filter:
        assignments = assignments.filter(assigned_at__date=date_filter)

    # Unassigned orders
    unassigned_orders = Order.objects.filter(
        delivery_assignment__isnull=True,
    ).exclude(status__in=['cancelled', 'delivered', 'completed']).order_by('-created_at')

    return render(request, 'delivery/admin_dashboard.html', {
        'assignments': assignments,
        'unassigned_orders': unassigned_orders,
        'status_filter': status_filter,
        'dp_filter': dp_filter,
        'date_filter': date_filter,
        'status_choices': DeliveryAssignment.STATUS_CHOICES,
    })


# ─────────────────────────────────────────────
# DELIVERY PERSON VIEWS
# ─────────────────────────────────────────────

@delivery_person_required
def delivery_home_view(request):
    """Mobile-optimised dashboard for delivery persons."""
    today = timezone.now().date()
    my_assignments = DeliveryAssignment.objects.filter(delivery_person=request.user)

    assigned_today = my_assignments.filter(assigned_at__date=today).exclude(status='cancelled').count()
    completed_today = my_assignments.filter(delivered_at__date=today, status='delivered').count()
    total_completed = my_assignments.filter(status='delivered').count()

    # Earnings = sum of delivered orders' totals
    total_earnings = my_assignments.filter(
        status='delivered'
    ).aggregate(total=Sum('order__total'))['total'] or 0

    today_earnings = my_assignments.filter(
        status='delivered', delivered_at__date=today
    ).aggregate(total=Sum('order__total'))['total'] or 0

    # Active assignments (not delivered/cancelled)
    active = my_assignments.filter(status__in=['assigned', 'picked_up', 'in_transit']).select_related('order')[:5]

    return render(request, 'delivery/home.html', {
        'assigned_today': assigned_today,
        'completed_today': completed_today,
        'total_completed': total_completed,
        'total_earnings': total_earnings,
        'today_earnings': today_earnings,
        'active_assignments': active,
    })


@delivery_person_required
def my_assignments_view(request):
    """List all assignments for the delivery person with status filter tabs."""
    assignments = DeliveryAssignment.objects.filter(
        delivery_person=request.user
    ).select_related('order').order_by('-assigned_at')

    status_filter = request.GET.get('status', '')
    if status_filter:
        assignments = assignments.filter(status=status_filter)

    # Counts for tabs
    counts = DeliveryAssignment.objects.filter(delivery_person=request.user).values('status').annotate(
        count=Count('id')
    )
    status_counts = {c['status']: c['count'] for c in counts}

    return render(request, 'delivery/assignments.html', {
        'assignments': assignments,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'status_choices': DeliveryAssignment.STATUS_CHOICES,
    })


@delivery_person_required
def assignment_detail_view(request, pk):
    """Full order details for a delivery assignment."""
    assignment = get_object_or_404(
        DeliveryAssignment.objects.select_related('order'),
        pk=pk, delivery_person=request.user,
    )
    order = assignment.order
    items = order.items.select_related('product').all()

    return render(request, 'delivery/assignment_detail.html', {
        'assignment': assignment,
        'order': order,
        'items': items,
    })


@delivery_person_required
def update_status_view(request, pk):
    """POST endpoint to update delivery status with transitions."""
    assignment = get_object_or_404(
        DeliveryAssignment, pk=pk, delivery_person=request.user
    )

    if request.method != 'POST':
        return redirect('delivery:assignment_detail', pk=pk)

    new_status = request.POST.get('new_status', '')
    note = request.POST.get('note', '')

    # Validate transitions
    valid_transitions = {
        'assigned': ['picked_up', 'cancelled'],
        'picked_up': ['in_transit', 'cancelled'],
        'in_transit': ['delivered', 'cancelled'],
    }
    allowed = valid_transitions.get(assignment.status, [])
    if new_status not in allowed:
        messages.error(request, f'Cannot change from "{assignment.get_status_display()}" to "{new_status}".')
        return redirect('delivery:assignment_detail', pk=pk)

    if new_status == 'cancelled':
        return redirect('delivery:cancel_delivery', pk=pk)

    # Apply transition
    now = timezone.now()
    assignment.status = new_status
    if note:
        assignment.notes = (assignment.notes + '\n' + note).strip()

    if new_status == 'picked_up':
        assignment.picked_up_at = now
        assignment.order.status = 'processing'
        assignment.order.save(update_fields=['status'])
        auto_add_tracking_event(
            assignment.order, 'processing',
            description='Order picked up by delivery person.',
            updated_by=request.user,
        )

    elif new_status == 'in_transit':
        assignment.order.status = 'out_for_delivery'
        assignment.order.save(update_fields=['status'])
        auto_add_tracking_event(
            assignment.order, 'out_for_delivery',
            description='Order is out for delivery.',
            updated_by=request.user,
        )

    elif new_status == 'delivered':
        assignment.delivered_at = now
        order = assignment.order
        order.status = 'delivered'
        # If COD, mark as paid
        if order.payment_method == 'cod':
            order.is_paid = True
            order.save(update_fields=['status', 'is_paid'])
        else:
            order.save(update_fields=['status'])
        auto_add_tracking_event(
            order, 'delivered',
            description='Order delivered successfully.',
            updated_by=request.user,
        )
        # Increment total deliveries
        profile = request.user.profile
        profile.total_deliveries += 1
        profile.save(update_fields=['total_deliveries'])

    assignment.save()
    messages.success(request, f'Status updated to "{assignment.get_status_display()}".')
    return redirect('delivery:assignment_detail', pk=pk)


@delivery_person_required
def cancel_delivery_view(request, pk):
    """Cancellation form with reasons."""
    assignment = get_object_or_404(
        DeliveryAssignment.objects.select_related('order'),
        pk=pk, delivery_person=request.user,
    )

    if assignment.status in ['delivered', 'cancelled']:
        messages.error(request, 'This delivery cannot be cancelled.')
        return redirect('delivery:assignment_detail', pk=pk)

    form = CancelDeliveryForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        now = timezone.now()
        assignment.status = 'cancelled'
        assignment.cancelled_at = now
        assignment.cancellation_reason = form.cleaned_data['reason']
        assignment.cancellation_by = request.user
        details = form.cleaned_data.get('details', '')
        if details:
            assignment.notes = (assignment.notes + '\nCancel: ' + details).strip()
        assignment.save()

        # Reset order to pending for reassignment
        order = assignment.order
        order.status = 'pending'
        order.save(update_fields=['status'])
        auto_add_tracking_event(
            order, 'pending',
            description=f'Delivery cancelled by {request.user.username}: {assignment.get_cancellation_reason_display()}. Order available for reassignment.',
            updated_by=request.user,
        )

        # Notify customer and admin by email
        reason_display = assignment.get_cancellation_reason_display()
        _send_cancellation_emails(order, reason_display)

        messages.success(request, 'Delivery cancelled. The order is now available for reassignment.')
        return redirect('delivery:my_assignments')

    return render(request, 'delivery/cancel_form.html', {
        'assignment': assignment,
        'form': form,
    })


def _send_cancellation_emails(order, reason):
    """Notify customer and admin about delivery cancellation."""
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@smartshop.com')
    subject = f'SmartShop — Delivery Update for Order #{order.order_number}'
    customer_message = (
        f'Dear {order.full_name},\n\n'
        f'Unfortunately, the delivery for your order #{order.order_number} has been cancelled.\n'
        f'Reason: {reason}\n\n'
        f'We are reassigning your order to another delivery partner. '
        f'You will be notified once a new delivery is scheduled.\n\n'
        f'Thank you for your patience.\nSmartShop Team'
    )
    send_mail(subject, customer_message, from_email, [order.email], fail_silently=True)

    admin_subject = f'Delivery Cancelled — Order #{order.order_number}'
    admin_message = (
        f'Delivery for order #{order.order_number} has been cancelled.\n'
        f'Reason: {reason}\n'
        f'Customer: {order.full_name} ({order.email})\n'
        f'Order Total: ₹{order.total}\n\n'
        f'The order has been reset to "pending" and needs reassignment.'
    )
    send_mail(admin_subject, admin_message, from_email, [from_email], fail_silently=True)
