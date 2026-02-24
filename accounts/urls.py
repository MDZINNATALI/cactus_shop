from django.urls import path
from . import views

urlpatterns = [
    path('register-choice/', views.register_choice, name='register_choice'),
    path('register-buyer/', views.register_buyer, name='register_buyer'),
    path('register-seller/', views.register_seller, name='register_seller'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]