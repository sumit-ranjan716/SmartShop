"""URL patterns for the products app."""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('brands/', views.brand_list_view, name='brand_list'),
    path('brands/<slug:slug>/', views.brand_detail_view, name='brand_detail'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('products/<slug:slug>/review/', views.add_review_view, name='add_review'),
    path('products/<slug:slug>/wishlist/', views.toggle_wishlist_view, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),

    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard_view, name='seller_dashboard'),
    path('seller/product/add/', views.seller_add_product_view, name='seller_add_product'),
    path('seller/product/<int:pk>/edit/', views.seller_edit_product_view, name='seller_edit_product'),
    path('seller/product/<int:pk>/delete/', views.seller_delete_product_view, name='seller_delete_product'),
]
