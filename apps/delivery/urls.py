"""URL patterns for the delivery app."""
from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Delivery person portal
    path('', views.delivery_home_view, name='delivery_home'),
    path('assignments/', views.my_assignments_view, name='my_assignments'),
    path('assignments/<int:pk>/', views.assignment_detail_view, name='assignment_detail'),
    path('assignments/<int:pk>/update/', views.update_status_view, name='update_status'),
    path('assignments/<int:pk>/cancel/', views.cancel_delivery_view, name='cancel_delivery'),

    # Admin / seller
    path('assign/<str:order_number>/', views.assign_delivery_view, name='assign_delivery'),
    path('admin-dashboard/', views.admin_delivery_dashboard_view, name='admin_dashboard'),
]
