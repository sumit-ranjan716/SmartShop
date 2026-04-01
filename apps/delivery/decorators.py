"""
Custom decorator to restrict views to delivery persons only.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def delivery_person_required(view_func):
    """Allow access only for users whose profile.is_delivery_person is True."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or not request.user.profile.is_delivery_person:
            messages.error(request, 'You do not have access to the delivery portal.')
            return redirect('products:product_list')
        return view_func(request, *args, **kwargs)
    return _wrapped
