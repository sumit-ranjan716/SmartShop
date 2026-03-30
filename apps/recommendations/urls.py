"""URL patterns for the recommendations app."""
from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('popular/', views.popular_products_view, name='popular'),
    path('similar/<int:product_id>/', views.similar_products_view, name='similar'),
    path('also-bought/<int:product_id>/', views.also_bought_view, name='also_bought'),
]
