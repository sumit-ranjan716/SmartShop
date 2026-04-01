from django.urls import path

from . import views

app_name = 'discounts'

urlpatterns = [
    path('dashboard/', views.discount_dashboard_view, name='dashboard'),
    path('discount/create/', views.create_discount_view, name='create_discount'),
    path('discount/<int:pk>/edit/', views.edit_discount_view, name='edit_discount'),
    path('discount/<int:pk>/delete/', views.delete_discount_view, name='delete_discount'),
    path('coupon/create/', views.create_coupon_view, name='create_coupon'),
    path('coupon/<int:pk>/edit/', views.edit_coupon_view, name='edit_coupon'),
    path('coupon/<int:pk>/delete/', views.delete_coupon_view, name='delete_coupon'),
    path('coupon/<int:pk>/stats/', views.coupon_stats_view, name='coupon_stats'),
    path('apply/', views.apply_coupon_view, name='apply_coupon'),
    path('remove/', views.remove_coupon_view, name='remove_coupon'),
]

