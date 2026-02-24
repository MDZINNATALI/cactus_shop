from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from .models import Product, Category, ProductReview

def product_list(request):
    products = Product.objects.filter(available=True, is_approved=True)
    
    # সার্চ
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # ক্যাটাগরি ফিল্টার
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # প্রাইস ফিল্টার
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # সর্টিং
    sort = request.GET.get('sort', '-created_at')
    products = products.order_by(sort)
    
    # ফিচার্ড প্রোডাক্ট
    featured_products = Product.objects.filter(
        available=True, 
        is_approved=True, 
        is_featured=True
    )[:4]
    
    # ক্যাটাগরি লিস্ট
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).filter(product_count__gt=0)
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'categories': categories,
        'total_products': products.count(),
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True, is_approved=True)
    
    # ভিউ কাউন্ট আপডেট
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # রিলেটেড প্রোডাক্ট
    related_products = Product.objects.filter(
        category=product.category, 
        available=True, 
        is_approved=True
    ).exclude(id=product.id)[:4]
    
    # রিভিউ
    reviews = product.reviews.filter(is_approved=True)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
    }
    return render(request, 'products/product_detail.html', context)

@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # চেক করি ইউজার আগে রিভিউ দিয়েছে কিনা
        existing_review = ProductReview.objects.filter(
            product=product, 
            user=request.user
        ).first()
        
        if existing_review:
            # আগের রিভিউ আপডেট
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.is_approved = False  # আবার অ্যাপ্রুভ করতে হবে
            existing_review.save()
            messages.success(request, 'আপনার রিভিউ আপডেট করা হয়েছে! অ্যাডমিন অ্যাপ্রুভ করবে।')
        else:
            # নতুন রিভিউ
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'আপনার রিভিউ জমা দেওয়া হয়েছে! অ্যাডমিন অ্যাপ্রুভ করবে।')
        
    return redirect('product_detail', slug=slug)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(
        category=category, 
        available=True, 
        is_approved=True
    )
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_products.html', context)

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Only seller or admin can delete
    if request.user == product.seller or request.user.is_superuser:
        product.delete()

    return redirect('dashboard')  # তোমার dashboard url name বসাও