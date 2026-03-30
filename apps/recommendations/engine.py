"""
Recommendation engine with three strategies:
1. Category-based:  Products from the same category
2. Popular:         Most-purchased products overall
3. Collaborative:   "People also bought" — products frequently co-purchased
"""
from django.db.models import Count, Q
from apps.products.models import Product
from apps.orders.models import Order, OrderItem


def get_category_recommendations(product, limit=8):
    """
    Return products from the same category, excluding the given product.
    """
    return (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .order_by('-created_at')[:limit]
    )


def get_popular_products(limit=8):
    """
    Return the most-purchased products based on order-item counts.
    """
    return (
        Product.objects
        .filter(is_active=True)
        .annotate(purchase_count=Count('order_items'))
        .order_by('-purchase_count')[:limit]
    )


def get_collaborative_recommendations(product, limit=8):
    """
    "People also bought" — find other products that appear in the same
    orders as the given product.
    """
    # Step 1: Get all orders that contain this product
    order_ids = (
        OrderItem.objects
        .filter(product=product)
        .values_list('order_id', flat=True)
    )

    if not order_ids:
        # Fallback to category-based if no order history exists
        return get_category_recommendations(product, limit)

    # Step 2: Find other products in those orders, ranked by frequency
    return (
        Product.objects
        .filter(order_items__order_id__in=order_ids, is_active=True)
        .exclude(pk=product.pk)
        .annotate(co_purchase_count=Count('order_items'))
        .order_by('-co_purchase_count')[:limit]
    )


def get_personalized_recommendations(user, limit=8):
    """
    Recommend products based on the user's past purchases.
    Finds categories the user buys from most and suggests products
    from those categories that haven't been purchased yet.
    """
    if not user.is_authenticated:
        return get_popular_products(limit)

    # Get products the user has already purchased
    purchased_product_ids = (
        OrderItem.objects
        .filter(order__user=user)
        .values_list('product_id', flat=True)
    )

    if not purchased_product_ids:
        return get_popular_products(limit)

    # Get the categories the user buys from
    purchased_categories = (
        Product.objects
        .filter(pk__in=purchased_product_ids)
        .values_list('category_id', flat=True)
        .distinct()
    )

    # Recommend products from those categories that weren't purchased
    recommendations = (
        Product.objects
        .filter(category_id__in=purchased_categories, is_active=True)
        .exclude(pk__in=purchased_product_ids)
        .annotate(purchase_count=Count('order_items'))
        .order_by('-purchase_count')[:limit]
    )

    if recommendations.count() < limit:
        # Supplement with popular products
        existing_ids = list(recommendations.values_list('pk', flat=True))
        extra = (
            get_popular_products(limit)
            .exclude(pk__in=existing_ids + list(purchased_product_ids))
        )
        recommendations = list(recommendations) + list(extra)[:limit - len(recommendations)]

    return recommendations
