from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from products.models import Product, ProductReview

@login_required
def dashboard(request):
    """ক্রেতার ড্যাশবোর্ড"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    # সাম্প্রতিক অর্ডার
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # পরিসংখ্যান
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='PENDING').count()
    delivered_orders = Order.objects.filter(user=request.user, status='DELIVERED').count()
    
    # উইশলিস্ট (যদি পরে implement করি)
    # wishlist_items = Wishlist.objects.filter(user=request.user).count()
    
    # রিভিউ (যদি পরে implement করি)
    # reviews_count = ProductReview.objects.filter(user=request.user).count()
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        # 'wishlist_count': wishlist_items,
        # 'reviews_count': reviews_count,
    }
    return render(request, 'buyer/dashboard.html', context)

@login_required
def profile(request):
    """ক্রেতার প্রোফাইল দেখা ও এডিট"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    if request.method == 'POST':
        # প্রোফাইল আপডেট
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', '')
        user.save()
        
        messages.success(request, 'আপনার প্রোফাইল সফলভাবে আপডেট হয়েছে!')
        return redirect('buyer_profile')
    
    return render(request, 'buyer/profile.html')

@login_required
def order_history(request):
    """ক্রেতার অর্ডার হিস্টোরি"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'buyer/order_history.html', context)

@login_required
def wishlist(request):
    """ক্রেতার উইশলিস্ট"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    # TODO: Wishlist মডেল তৈরি করে implement করতে হবে
    # wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        # 'wishlist_items': wishlist_items,
    }
    return render(request, 'buyer/wishlist.html', context)

@login_required
def reviews(request):
    """ক্রেতার দেওয়া রিভিউ"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    reviews = ProductReview.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reviews': reviews,
    }
    return render(request, 'buyer/reviews.html', context)

@login_required
def settings(request):
    """ক্রেতার সেটিংস"""
    if request.user.user_type != 'BUYER':
        messages.error(request, 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই!')
        return redirect('home')
    
    if request.method == 'POST':
        # পাসওয়ার্ড পরিবর্তন
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'পুরোনো পাসওয়ার্ড সঠিক নয়!')
        elif new_password != confirm_password:
            messages.error(request, 'নতুন পাসওয়ার্ড মিলছে না!')
        elif len(new_password) < 6:
            messages.error(request, 'পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'আপনার পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে!')
            return redirect('login')
    
    return render(request, 'buyer/settings.html')