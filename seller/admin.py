from django.contrib import admin
from .models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):

    list_display = ['user', 'created_at']
    search_fields = ['user__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']