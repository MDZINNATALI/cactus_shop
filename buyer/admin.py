from django.contrib import admin
from .models import Buyer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'created_at'
    ]

    search_fields = [
        'user__username'
    ]

    list_filter = [
        'created_at'
    ]

    readonly_fields = ['created_at']