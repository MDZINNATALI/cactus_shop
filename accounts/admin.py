from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SellerProfile


# ===============================
# 🔵 Custom User Admin
# ===============================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = [
        'username',
        'email',
        'user_type',
        'is_approved',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'user_type',
        'is_approved',
        'is_active'
    ]

    search_fields = [
        'username',
        'email',
        'phone'
    ]

    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {
            'fields': (
                'user_type',
                'phone',
                'address',
                'profile_pic',
                'is_approved'
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {
            'fields': (
                'user_type',
                'phone',
                'address',
                'email',
            )
        }),
    )
    def delete_model(self, request, obj):
        obj.delete()

# ===============================
# 🔵 Seller Profile Admin
# ===============================

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):

    list_display = [
        'store_name',
        'user',
        'nid_number',
        'payment_method',
        'rating',
        'is_active'
    ]

    list_filter = [
        'payment_method',
        'is_active',
        'created_at'
    ]

    search_fields = [
        'store_name',
        'user__username',
        'nid_number'
    ]

    readonly_fields = ['created_at']