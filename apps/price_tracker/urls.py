from django.urls import path
from . import views

app_name = 'price_tracker'

urlpatterns = [
    path('api/toggle-alert/<int:product_id>/', views.toggle_price_alert_view, name='toggle_alert'),
    path('api/history/<int:product_id>/', views.price_history_api, name='price_history_api'),
    path('my-alerts/', views.my_alerts_view, name='my_alerts'),
    path('wishlist/shared/<uuid:token>/', views.shared_wishlist_view, name='shared_wishlist'),
]
