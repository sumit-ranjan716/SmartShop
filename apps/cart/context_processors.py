"""
Context processor to make cart item count available in all templates.
"""
from .models import Cart


def cart_count(request):
    """Return cart item count for navbar badge."""
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None

        if cart:
            count = cart.total_items
    except Exception:
        pass

    return {'cart_item_count': count}
