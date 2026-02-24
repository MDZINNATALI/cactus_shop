from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Total Products'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2

class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail', 'name', 'seller', 'category', 
        'get_price', 'stock', 'is_approved', 'is_featured', 'created_at'
    ]
    list_filter = ['is_approved', 'is_featured', 'available', 'category', 'created_at']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['name', 'description', 'seller__username']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['views_count', 'sold_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline, ProductReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'category', 'name', 'slug', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Images', {
            'fields': ('image', 'image2', 'image3')
        }),
        ('Status', {
            'fields': ('available', 'is_approved', 'is_featured', 'is_new')
        }),
        ('Statistics', {
            'fields': ('views_count', 'sold_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;">'.format(obj.image.url))
        return 'No Image'
    thumbnail.short_description = 'Image'
    
    def get_price(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="color:red; text-decoration:line-through;">৳{}</span> ৳{}'.format(
                    obj.price, obj.discount_price
                )
            )
        return f'৳{obj.price}'
    get_price.short_description = 'Price'
    
    def save_model(self, request, obj, form, change):
        if not change:  # নতুন প্রোডাক্ট হলে
            obj.is_new = True
        super().save_model(request, obj, form, change)

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']