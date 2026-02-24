from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('BUYER', 'Buyer'),
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    )
    
    # কনফ্লিক্ট এড়ানোর জন্য related_name যোগ করা হয়েছে
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    # কাস্টম ফিল্ড
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='BUYER')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Seller approval এর জন্য
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # ✅ এই অংশটা যোগ করো: superuser হলে automatically ADMIN হবে
        if self.is_superuser:
            self.user_type = 'ADMIN'
            self.is_approved = True
            self.is_staff = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    store_name = models.CharField(max_length=200)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to='stores/logos/', blank=True, null=True)
    business_address = models.TextField()
    nid_number = models.CharField(max_length=20)
    trade_license = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=100, choices=(
        ('BKASH', 'বিকাশ'),
        ('NAGAD', 'নগদ'),
        ('ROCKET', 'রকেট'),
        ('BANK', 'ব্যাংক'),
    ))
    payment_number = models.CharField(max_length=20)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_products = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.store_name