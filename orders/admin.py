from django.utils import timezone
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem, OrderStatusHistory, OrderPayment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'item_total']
    fields = ['product', 'product_name', 'product_price', 'quantity', 'item_total']
    
    def item_total(self, obj):
        return f"৳{obj.total_price}"
    item_total.short_description = 'Total'

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'notes', 'created_by', 'created_at']
    fields = ['status', 'notes', 'created_by', 'created_at']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'phone', 'total_amount', 
        'payment_status_display', 'status_display', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'phone', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'delivered_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('অর্ডার তথ্য', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('ক্রেতার তথ্য', {
            'fields': ('full_name', 'email', 'phone', 'alternative_phone')
        }),
        ('ঠিকানা', {
            'fields': ('address', 'city', 'area', 'postal_code')
        }),
        ('পেমেন্ট তথ্য', {
            'fields': ('payment_method', 'payment_status', 'transaction_id', 
                      'total_amount', 'shipping_cost', 'discount_amount', 'coupon_code')
        }),
        ('অন্যান্য', {
            'fields': ('customer_notes', 'created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def customer(self, obj):
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return obj.full_name
    customer.short_description = 'ক্রেতা'
    
    def status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'PROCESSING': 'purple',
            'SHIPPED': 'teal',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
            'RETURNED': 'gray',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'স্ট্যাটাস'
    
    def payment_status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'PAID': 'green',
            'FAILED': 'red',
            'REFUNDED': 'blue',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.payment_status, 'black'),
            obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'পেমেন্ট'
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='CONFIRMED')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='CONFIRMED',
                notes='অ্যাডমিন দ্বারা কনফার্মড',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()}টি অর্ডার কনফার্ম করা হয়েছে।")
    mark_as_confirmed.short_description = "✅ সিলেক্টেড অর্ডার কনফার্ম করুন"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='SHIPPED',
                notes='অ্যাডমিন দ্বারা শিপড',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()}টি অর্ডার শিপ করা হয়েছে।")
    mark_as_shipped.short_description = "🚚 সিলেক্টেড অর্ডার শিপ করুন"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='DELIVERED', delivered_at=timezone.now())
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='DELIVERED',
                notes='অ্যাডমিন দ্বারা ডেলিভারড',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()}টি অর্ডার ডেলিভার করা হয়েছে।")
    mark_as_delivered.short_description = "📦 সিলেক্টেড অর্ডার ডেলিভার করুন"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        for order in queryset:
            OrderStatusHistory.objects.create(
                order=order,
                status='CANCELLED',
                notes='অ্যাডমিন দ্বারা ক্যান্সেলড',
                created_by=request.user
            )
        self.message_user(request, f"{queryset.count()}টি অর্ডার ক্যান্সেল করা হয়েছে।")
    mark_as_cancelled.short_description = "❌ সিলেক্টেড অর্ডার ক্যান্সেল করুন"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_link', 'product_name', 'quantity', 'price', 'total', 'seller']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product_name', 'seller__username']
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">#{}</a>', url, obj.order.order_number)
    order_link.short_description = 'অর্ডার'
    
    def price(self, obj):
        return f"৳{obj.product_price}"
    price.short_description = 'দাম'
    
    def total(self, obj):
        return f"৳{obj.total_price}"
    total.short_description = 'মোট'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status_display', 'notes', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'notes']
    
    def status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'PROCESSING': 'purple',
            'SHIPPED': 'teal',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
            'RETURNED': 'gray',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_display.short_description = 'স্ট্যাটাস'