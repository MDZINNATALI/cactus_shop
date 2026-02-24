from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'item_total']
    
    def item_total(self, obj):
        return f"৳{obj.total_price}"
    item_total.short_description = 'Total'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'items_count', 'subtotal', 'shipping', 'total', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    def items_count(self, obj):
        return obj.total_items
    items_count.short_description = 'Items'
    
    def subtotal(self, obj):
        return f"৳{obj.subtotal}"
    subtotal.short_description = 'Subtotal'
    
    def shipping(self, obj):
        return f"৳{obj.shipping_cost}"
    shipping.short_description = 'Shipping'
    
    def total(self, obj):
        return format_html('<b>৳{}</b>', obj.total)
    total.short_description = 'Total'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def unit_price(self, obj):
        return f"৳{obj.product.get_display_price()}"
    unit_price.short_description = 'Price'
    
    def total_price(self, obj):
        return f"৳{obj.total_price}"
    total_price.short_description = 'Total'