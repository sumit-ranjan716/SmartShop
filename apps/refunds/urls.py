from django.urls import path

from . import views

app_name = 'refunds'

urlpatterns = [
    path('request/refund/<str:order_number>/', views.request_refund_view, name='request_refund'),
    path('request/exchange/<str:order_number>/', views.request_exchange_view, name='request_exchange'),
    path('my/', views.my_requests_view, name='my_requests'),
    path('detail/<str:request_type>/<int:pk>/', views.request_detail_view, name='request_detail'),
    path('seller/', views.seller_refund_requests_view, name='seller_requests'),
    path('seller/refund/<int:pk>/approve/', views.seller_approve_refund_view, name='seller_approve_refund'),
    path('seller/refund/<int:pk>/reject/', views.seller_reject_refund_view, name='seller_reject_refund'),
    path('seller/exchange/<int:pk>/approve/', views.seller_approve_exchange_view, name='seller_approve_exchange'),
    path('seller/exchange/<int:pk>/reject/', views.seller_reject_exchange_view, name='seller_reject_exchange'),
]

