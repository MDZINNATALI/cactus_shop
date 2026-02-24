from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import User, SellerProfile
from products.models import Product, Category, ProductReview
from orders.models import Order, OrderItem

@staff_member_required
def dashboard(request):
    """অ্যাডমিন ড্যাশবোর্ড"""
    if not request.user.is_staff:
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    # পরিসংখ্যান
    total_users = User.objects.count()
    total_buyers = User.objects.filter(user_type='BUYER').count()
    total_sellers = User.objects.filter(user_type='SELLER').count()
    pending_sellers = User.objects.filter(user_type='SELLER', is_approved=False).count()
    
    total_products = Product.objects.count()
    pending_products = Product.objects.filter(is_approved=False).count()
    out_of_stock = Product.objects.filter(stock=0).count()
    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    total_revenue = Order.objects.filter(status='DELIVERED').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # চার্টের জন্য ডাটা
    last_7_days_orders = []
    for i in range(7):
        date = timezone.now().date() - timezone.timedelta(days=i)
        count = Order.objects.filter(created_at__date=date).count()
        last_7_days_orders.append({
            'date': date.strftime('%d %b'),
            'count': count
        })
    
    context = {
        'total_users': total_users,
        'total_buyers': total_buyers,
        'total_sellers': total_sellers,
        'pending_sellers': pending_sellers,
        'total_products': total_products,
        'pending_products': pending_products,
        'out_of_stock': out_of_stock,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'last_7_days_orders': last_7_days_orders,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@staff_member_required
def pending_sellers(request):
    """পেন্ডিং সেলারদের তালিকা"""
    sellers = User.objects.filter(user_type='SELLER', is_approved=False).select_related('seller_profile')
    
    if request.method == 'POST':
        seller_id = request.POST.get('seller_id')
        action = request.POST.get('action')
        
        seller = get_object_or_404(User, id=seller_id, user_type='SELLER')
        
        if action == 'approve':
            seller.is_approved = True
            seller.save()
            messages.success(request, f'{seller.username} এর অ্যাকাউন্ট অ্যাপ্রুভ করা হয়েছে!')
        elif action == 'reject':
            reason = request.POST.get('reason', '')
            # seller.delete()  # অথবা রিজেক্ট করুন
            messages.warning(request, f'{seller.username} এর অ্যাকাউন্ট রিজেক্ট করা হয়েছে!')
        
        return redirect('admin_pending_sellers')
    
    context = {
        'sellers': sellers,
    }
    return render(request, 'admin_dashboard/pending_sellers.html', context)

@staff_member_required
def pending_products(request):
    """পেন্ডিং পণ্যের তালিকা"""
    products = Product.objects.filter(is_approved=False).select_related('seller', 'category')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        
        product = get_object_or_404(Product, id=product_id)
        
        if action == 'approve':
            product.is_approved = True
            product.save()
            messages.success(request, f'{product.name} অ্যাপ্রুভ করা হয়েছে!')
        elif action == 'reject':
            reason = request.POST.get('reason', '')
            product.delete()
            messages.warning(request, f'{product.name} রিজেক্ট ও ডিলিট করা হয়েছে!')
        
        return redirect('admin_pending_products')
    
    context = {
        'products': products,
    }
    return render(request, 'admin_dashboard/pending_products.html', context)

@staff_member_required
def all_sellers(request):
    """সব সেলারের তালিকা"""
    sellers = User.objects.filter(user_type='SELLER').select_related('seller_profile').order_by('-date_joined')
    
    # সার্চ
    query = request.GET.get('q')
    if query:
        sellers = sellers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(seller_profile__store_name__icontains=query)
        )
    
    context = {
        'sellers': sellers,
    }
    return render(request, 'admin_dashboard/all_sellers.html', context)

@staff_member_required
def all_products(request):
    """সব পণ্যের তালিকা"""
    products = Product.objects.all().select_related('seller', 'category').order_by('-created_at')
    
    # ফিল্টার
    seller_id = request.GET.get('seller')
    if seller_id:
        products = products.filter(seller_id=seller_id)
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    context = {
        'products': products,
    }
    return render(request, 'admin_dashboard/all_products.html', context)

@staff_member_required
def all_orders(request):
    """সব অর্ডারের তালিকা"""
    orders = Order.objects.all().order_by('-created_at')
    
    # ফিল্টার
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
    }
    return render(request, 'admin_dashboard/all_orders.html', context)

@staff_member_required
def order_detail(request, order_id):
    """অর্ডার ডিটেইল"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'অর্ডার #{order.order_number} এর স্ট্যাটাস আপডেট হয়েছে!')
        return redirect('admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
    }
    return render(request, 'admin_dashboard/order_detail.html', context)

@staff_member_required
def all_users(request):
    """সব ইউজারের তালিকা"""
    users = User.objects.all().order_by('-date_joined')
    
    # ফিল্টার
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    context = {
        'users': users,
    }
    return render(request, 'admin_dashboard/all_users.html', context)

@staff_member_required
def reports(request):
    """রিপোর্ট ও অ্যানালিটিক্স"""
    # মাসিক বিক্রয় রিপোর্ট
    monthly_sales = []
    for i in range(6):
        month = timezone.now().date() - timezone.timedelta(days=30*i)
        sales = Order.objects.filter(
            status='DELIVERED',
            created_at__month=month.month,
            created_at__year=month.year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_sales.append({
            'month': month.strftime('%B %Y'),
            'sales': sales
        })
    
    # ক্যাটাগরি অনুযায়ী বিক্রয়
    category_sales = Category.objects.annotate(
        total_sold=Sum('products__sold_count')
    ).order_by('-total_sold')[:5]
    
    # টপ সেলার
    top_sellers = User.objects.filter(
        user_type='SELLER'
    ).annotate(
        total_sales=Sum('seller_order_items__total_price'),
        total_orders=Count('seller_order_items', distinct=True)
    ).order_by('-total_sales')[:10]
    
    context = {
        'monthly_sales': monthly_sales,
        'category_sales': category_sales,
        'top_sellers': top_sellers,
    }
    return render(request, 'admin_dashboard/reports.html', context)

@staff_member_required
def settings(request):
    """অ্যাডমিন সেটিংস"""
    if request.method == 'POST':
        # সেটিংস আপডেট
        messages.success(request, 'সেটিংস আপডেট হয়েছে!')
        return redirect('admin_settings')
    
    return render(request, 'admin_dashboard/settings.html')