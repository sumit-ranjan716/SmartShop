"""
ecommerce_project URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('users/', include('apps.users.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('discounts/', include('apps.discounts.urls')),
    path('refunds/', include('apps.refunds.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('delivery/', include('apps.delivery.urls')),
    path('price-tracker/', include('apps.price_tracker.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
