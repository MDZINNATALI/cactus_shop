from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='seller_dashboard'),
    path('products/', views.products, name='seller_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.orders, name='seller_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='seller_order_detail'),
    path('orders/<int:order_id>/item/<int:item_id>/update/', views.update_order_status, name='update_order_status'),
    path('reviews/', views.reviews, name='seller_reviews'),
    path('settings/', views.settings, name='seller_settings'),
]