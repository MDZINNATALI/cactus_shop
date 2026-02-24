from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', '📝 পেন্ডিং'),
        ('CONFIRMED', '✅ কনফার্মড'),
        ('PROCESSING', '⚙️ প্রসেসিং'),
        ('SHIPPED', '🚚 শিপড'),
        ('DELIVERED', '📦 ডেলিভারড'),
        ('CANCELLED', '❌ ক্যান্সেলড'),
        ('RETURNED', '🔄 রিটার্নড'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('BKASH', '📱 বিকাশ'),
        ('NAGAD', '📱 নগদ'),
        ('ROCKET', '🚀 রকেট'),
        ('CARD', '💳 কার্ড'),
        ('CASH', '💰 ক্যাশ অন ডেলিভারি'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', '⏳ পেন্ডিং'),
        ('PAID', '💵 পেইড'),
        ('FAILED', '❌ ফেইলড'),
        ('REFUNDED', '💰 রিফান্ডেড'),
    )
    
    # ইউজার ইনফো
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='orders'
    )
    
    # কন্টাক্ট ইনফো
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    
    # অ্যাড্রেস
    address = models.TextField()
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # অর্ডার ইনফো
    order_number = models.CharField(max_length=50, unique=True, default='TEMP-ORDER')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=50)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True)
    
    # পেমেন্ট
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # স্ট্যাটাস
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, help_text="অ্যাডমিনের জন্য নোট")
    customer_notes = models.TextField(blank=True, help_text="ক্রেতার বিশেষ অনুরোধ")
    
    # টাইমস্ট্যাম্প
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # অর্ডার নম্বর জেনারেট: ORD-2024-00001
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
                self.order_number = f"ORD-{self.created_at.year}-{last_id+1:05d}"
            else:
                self.order_number = f"ORD-{self.created_at.year}-00001"
        super().save(*args, **kwargs)
    
    @property
    def subtotal(self):
        return self.total_amount - self.shipping_cost + self.discount_amount
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def is_paid(self):
        return self.payment_status == 'PAID'
    
    @property
    def can_cancel(self):
        return self.status in ['PENDING', 'CONFIRMED']

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    
    # প্রোডাক্ট স্ন্যাপশট (প্রাইস পরিবর্তন হলে)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.CharField(max_length=500, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seller_order_items'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    @property
    def total_price(self):
        return self.product_price * self.quantity
    
    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.name
            self.product_price = self.product.get_display_price()
            self.seller = self.product.seller
            if self.product.image:
                self.product_image = self.product.image.url
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

class OrderPayment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=Order.PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=Order.PAYMENT_STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.amount}"