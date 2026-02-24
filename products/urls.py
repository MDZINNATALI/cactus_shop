from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]