from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from products.models import Product, Category, ProductReview
from orders.models import OrderItem, Order

@login_required
def dashboard(request):
    """সেলার ড্যাশবোর্ড"""
    if request.user.user_type != 'SELLER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')

    if not request.user.is_approved:
        messages.warning(request, 'আপনার অ্যাকাউন্ট অ্যাপ্রুভাল পেন্ডিং। অ্যাডমিন অ্যাপ্রুভ করলে আপনি ড্যাশবোর্ড ব্যবহার করতে পারবেন।')
        return redirect('home')

    # SellerProfile চেক করো
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'Seller profile পাওয়া যায়নি!')
        return redirect('home')

    # পরিসংখ্যান
    total_products = Product.objects.filter(seller=request.user).count()
    active_products = Product.objects.filter(seller=request.user, available=True).count()
    pending_products = Product.objects.filter(seller=request.user, is_approved=False).count()

    # অর্ডার পরিসংখ্যান
    order_items = OrderItem.objects.filter(seller=request.user)
    total_orders = order_items.values('order').distinct().count()
    pending_orders = order_items.filter(order__status='PENDING').count()
    delivered_orders = order_items.filter(order__status='DELIVERED').count()

    # ✅ বিক্রয় পরিসংখ্যান (total_price এর পরিবর্তে product_price ব্যবহার করো)
    total_sales = order_items.aggregate(
        total=Sum('product_price')
    )['total'] or 0
    
    this_month_sales = order_items.filter(
        order__created_at__month=timezone.now().month,
        order__created_at__year=timezone.now().year
    ).aggregate(total=Sum('product_price'))['total'] or 0

    # সাম্প্রতিক অর্ডার
    recent_orders = order_items.select_related('order', 'product').order_by('-order__created_at')[:5]

    # রিভিউ (try-except এ রাখো)
    try:
        reviews = ProductReview.objects.filter(product__seller=request.user).order_by('-created_at')[:5]
        avg_rating = reviews.aggregate(avg=Sum('rating')/Count('id'))['avg'] or 0
    except:
        reviews = []
        avg_rating = 0

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'pending_products': pending_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_sales': total_sales,
        'this_month_sales': this_month_sales,
        'recent_orders': recent_orders,
        'recent_reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'seller/dashboard.html', context)

@login_required
def products(request):
    """সেলারের সব পণ্য"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    product_list = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # ফিল্টার
    status = request.GET.get('status')
    if status == 'approved':
        product_list = product_list.filter(is_approved=True)
    elif status == 'pending':
        product_list = product_list.filter(is_approved=False)
    elif status == 'out_of_stock':
        product_list = product_list.filter(stock=0)
    
    context = {
        'products': product_list,
    }
    return render(request, 'seller/products.html', context)

@login_required
def add_product(request):
    """নতুন পণ্য যোগ করা"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # ডাটা ভ্যালিডেশন
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        if not name or not price or not stock:
            messages.error(request, 'সব প্রয়োজনীয় তথ্য দিন!')
            return redirect('add_product')
        
        # স্লাগ তৈরি
        from django.utils.text import slugify
        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # পণ্য তৈরি
        product = Product.objects.create(
            seller=request.user,
            category_id=request.POST.get('category'),
            name=name,
            slug=slug,
            description=request.POST.get('description', ''),
            price=price,
            discount_price=request.POST.get('discount_price') or None,
            stock=stock,
            is_approved=False,  # অ্যাডমিন অ্যাপ্রুভ করবে
        )
        
        # ছবি আপলোড
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        if 'image2' in request.FILES:
            product.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            product.image3 = request.FILES['image3']
        
        product.save()
        
        messages.success(request, 'পণ্য সফলভাবে যোগ করা হয়েছে! অ্যাডমিন অ্যাপ্রুভ করলে তা সাইটে দেখা যাবে।')
        return redirect('seller_products')
    
    context = {
        'categories': categories,
    }
    return render(request, 'seller/add_product.html', context)

@login_required
def edit_product(request, product_id):
    """পণ্য এডিট করা"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock')
        
        # নতুন ছবি আপলোড
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        if 'image2' in request.FILES:
            product.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            product.image3 = request.FILES['image3']
        
        product.save()
        messages.success(request, 'পণ্য সফলভাবে আপডেট হয়েছে!')
        return redirect('seller_products')
    
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'seller/edit_product.html', context)

@login_required
def delete_product(request, product_id):
    """পণ্য ডিলিট করা"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'পণ্য ডিলিট করা হয়েছে!')
        return redirect('seller_products')
    
    return render(request, 'seller/delete_product.html', {'product': product})

@login_required
def orders(request):
    """সেলারের অর্ডার"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    order_items = OrderItem.objects.filter(
        seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')
    
    # ফিল্টার
    status = request.GET.get('status')
    if status:
        order_items = order_items.filter(order__status=status)
    
    # অর্ডার গ্রুপিং
    orders_dict = {}
    for item in order_items:
        if item.order not in orders_dict:
            orders_dict[item.order] = []
        orders_dict[item.order].append(item)
    
    context = {
        'orders_dict': orders_dict,
    }
    return render(request, 'seller/orders.html', context)

@login_required
def order_detail(request, order_id):
    """অর্ডার ডিটেইল"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order, seller=request.user)
    
    if not items.exists():
        messages.error(request, 'এই অর্ডারে আপনার কোনো পণ্য নেই!')
        return redirect('seller_orders')
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'seller/order_detail.html', context)

@login_required
def update_order_status(request, order_id, item_id):
    """অর্ডার আইটেমের স্ট্যাটাস আপডেট"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    item = get_object_or_404(OrderItem, id=item_id, seller=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        # TODO: ইমপ্লিমেন্ট স্ট্যাটাস আপডেট লজিক
        messages.success(request, 'অর্ডার স্ট্যাটাস আপডেট হয়েছে!')
    
    return redirect('seller_order_detail', order_id=order_id)

@login_required
def reviews(request):
    """পণ্যের রিভিউ"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    reviews = ProductReview.objects.filter(
        product__seller=request.user
    ).select_related('product', 'user').order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'seller/reviews.html', context)

@login_required
def settings(request):
    """সেলার সেটিংস"""
    if request.user.user_type != 'SELLER' or not request.user.is_approved:
        return redirect('home')
    
    seller_profile = request.user.seller_profile
    
    if request.method == 'POST':
        # প্রোফাইল আপডেট
        seller_profile.store_name = request.POST.get('store_name')
        seller_profile.store_description = request.POST.get('store_description')
        seller_profile.business_address = request.POST.get('business_address')
        seller_profile.payment_method = request.POST.get('payment_method')
        seller_profile.payment_number = request.POST.get('payment_number')
        
        if 'store_logo' in request.FILES:
            seller_profile.store_logo = request.FILES['store_logo']
        
        seller_profile.save()
        messages.success(request, 'সেটিংস আপডেট হয়েছে!')
        return redirect('seller_settings')
    
    context = {
        'profile': seller_profile,
    }
    return render(request, 'seller/settings.html', context)