"""
Views for the recommendations app — JSON API endpoints.
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from apps.products.models import Product
from . import engine


def popular_products_view(request):
    """Return popular products as JSON."""
    products = engine.get_popular_products(limit=8)
    data = [
        {
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': str(p.price),
            'image': p.image.url if p.image else '',
        }
        for p in products
    ]
    return JsonResponse({'products': data})


def similar_products_view(request, product_id):
    """Return category-based recommendations as JSON."""
    product = get_object_or_404(Product, pk=product_id)
    products = engine.get_category_recommendations(product, limit=8)
    data = [
        {
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': str(p.price),
            'image': p.image.url if p.image else '',
        }
        for p in products
    ]
    return JsonResponse({'products': data})


def also_bought_view(request, product_id):
    """Return collaborative recommendations as JSON."""
    product = get_object_or_404(Product, pk=product_id)
    products = engine.get_collaborative_recommendations(product, limit=8)
    data = [
        {
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': str(p.price),
            'image': p.image.url if p.image else '',
        }
        for p in products
    ]
    return JsonResponse({'products': data})
