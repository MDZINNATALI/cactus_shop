from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_views.product_list, name='home'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('buyer/', include('buyer.urls')),
    path('seller/', include('seller.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
]

# মিডিয়া ফাইল সার্ভ করার জন্য (শুধু ডেভেলপমেন্টে)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)