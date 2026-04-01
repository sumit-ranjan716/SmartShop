"""URL patterns for the orders app."""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('history/', views.order_history_view, name='order_history'),
    path('<str:order_number>/stripe-intent/', views.create_stripe_payment_intent_view, name='create_stripe_intent'),
    path('<str:order_number>/upi-qr/', views.generate_upi_qr_view, name='generate_upi_qr'),
    path('<str:order_number>/upi-confirm/', views.confirm_upi_payment_view, name='confirm_upi_payment'),
    path('<str:order_number>/tracking/', views.order_tracking_view, name='order_tracking'),
    path('<str:order_number>/tracking/status/', views.order_tracking_status_view, name='order_tracking_status'),
    path('<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
]
