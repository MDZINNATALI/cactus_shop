from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='buyer_dashboard'),
    path('profile/', views.profile, name='buyer_profile'),
    path('orders/', views.order_history, name='buyer_orders'),
    path('wishlist/', views.wishlist, name='buyer_wishlist'),
    path('reviews/', views.reviews, name='buyer_reviews'),
    path('settings/', views.settings, name='buyer_settings'),
]