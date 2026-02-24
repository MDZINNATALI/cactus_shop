from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('pending-sellers/', views.pending_sellers, name='admin_pending_sellers'),
    path('pending-products/', views.pending_products, name='admin_pending_products'),
    path('all-sellers/', views.all_sellers, name='admin_all_sellers'),
    path('all-products/', views.all_products, name='admin_all_products'),
    path('all-orders/', views.all_orders, name='admin_all_orders'),
    path('order/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('all-users/', views.all_users, name='admin_all_users'),
    path('reports/', views.reports, name='admin_reports'),
    path('settings/', views.settings, name='admin_settings'),
]