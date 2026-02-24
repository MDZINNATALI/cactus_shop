from django.db import models
from django.conf import settings
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])

class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'SELLER'},
        related_name='products'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=0)
    
    # পণ্যের বিবরণ
    specifications = models.JSONField(default=dict, blank=True)  # যেমন: {'height': '4 inch', 'pot': 'clay'}
    
    # স্ট্যাটাস
    available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # অ্যাডমিন অ্যাপ্রুভাল
    is_featured = models.BooleanField(default=False)  # হোমপেজে দেখানোর জন্য
    is_new = models.BooleanField(default=True)
    
    # মেটা ডাটা
    views_count = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)
    
    # টাইমস্ট্যাম্প
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['seller', 'is_approved']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.seller.username}"
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])
    
    def get_display_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def get_discount_percentage(self):
        if self.discount_price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount)
        return 0
    
    @property
    def is_in_stock(self):
        return self.stock > 0
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='products/extra/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # এক ইউজার একবার রিভিউ দিতে পারবে
    
    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"