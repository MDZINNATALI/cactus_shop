from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem, OrderStatusHistory

@login_required
def order_list(request):
    """ইউজারের সব অর্ডার দেখানো"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    
    context = {
        'orders': orders,
        'pending_count': orders.filter(status='PENDING').count(),
        'delivered_count': orders.filter(status='DELIVERED').count(),
        'cancelled_count': orders.filter(status='CANCELLED').count(),
    }
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_number):
    """অর্ডারের বিস্তারিত দেখানো"""
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        user=request.user
    )
    
    context = {
        'order': order,
        'status_history': order.status_history.all()[:5],
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def checkout(request):
    """চেকআউট পেজ - অর্ডার কনফার্মেশনের আগে"""
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.warning(request, 'আপনার কার্ট খালি!')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        # অর্ডার তৈরি প্রসেস শুরু
        return place_order(request)
    
    # ইউজারের প্রোফাইল থেকে ডিফল্ট ইনফো নেওয়া
    initial_data = {
        'full_name': request.user.get_full_name(),
        'email': request.user.email,
        'phone': request.user.phone,
        'address': request.user.address,
    }
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'subtotal': cart.subtotal,
        'shipping_cost': cart.shipping_cost,
        'total': cart.total,
        'initial': initial_data,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
@transaction.atomic
def place_order(request):
    """অর্ডার প্লেস করা"""
    if request.method != 'POST':
        return redirect('checkout')
    
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, 'আপনার কার্ট খালি!')
        return redirect('cart_detail')
    
    # স্টক চেক
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(
                request, 
                f'{item.product.name} এর জন্য পর্যাপ্ত স্টক নেই! স্টক আছে: {item.product.stock}টি'
            )
            return redirect('cart_detail')
    
    # অর্ডার তৈরি
    order = Order.objects.create(
        user=request.user,
        full_name=request.POST.get('full_name'),
        email=request.POST.get('email'),
        phone=request.POST.get('phone'),
        alternative_phone=request.POST.get('alternative_phone', ''),
        address=request.POST.get('address'),
        city=request.POST.get('city', 'Dhaka'),
        area=request.POST.get('area', ''),
        postal_code=request.POST.get('postal_code', ''),
        total_amount=cart.total,
        shipping_cost=cart.shipping_cost,
        payment_method=request.POST.get('payment_method'),
        customer_notes=request.POST.get('notes', ''),
    )
    
    # অর্ডার আইটেম তৈরি
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
        
        # স্টক আপডেট
        product = item.product
        product.stock -= item.quantity
        product.sold_count += item.quantity
        product.save()
    
    # স্ট্যাটাস হিস্টোরি তৈরি
    OrderStatusHistory.objects.create(
        order=order,
        status='PENDING',
        notes='অর্ডার প্লেস করা হয়েছে',
        created_by=request.user
    )
    
    # কার্ট খালি করা
    cart.items.all().delete()
    
    # ইমেইল পাঠানো (ঐচ্ছিক)
    try:
        send_order_confirmation_email(order)
    except:
        pass
    
    messages.success(request, f'অর্ডার #{order.order_number} সফলভাবে প্লেস হয়েছে!')
    return redirect('order_detail', order_number=order.order_number)

@login_required
def cancel_order(request, order_number):
    """অর্ডার ক্যান্সেল করা"""
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        user=request.user
    )
    
    if not order.can_cancel:
        messages.error(request, 'এই অর্ডার ক্যান্সেল করা যাবে না!')
        return redirect('order_detail', order_number=order_number)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        with transaction.atomic():
            # স্টক ফেরত
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.sold_count -= item.quantity
                    item.product.save()
            
            # স্ট্যাটাস আপডেট
            order.status = 'CANCELLED'
            order.save()
            
            # হিস্টোরি
            OrderStatusHistory.objects.create(
                order=order,
                status='CANCELLED',
                notes=f'ক্রেতার অনুরোধে ক্যান্সেল। কারণ: {reason}',
                created_by=request.user
            )
        
        messages.success(request, f'অর্ডার #{order.order_number} ক্যান্সেল করা হয়েছে!')
        return redirect('order_detail', order_number=order_number)
    
    return render(request, 'orders/cancel_order.html', {'order': order})

@login_required
def track_order(request, order_number):
    """অর্ডার ট্র্যাক করা"""
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        user=request.user
    )
    
    context = {
        'order': order,
        'status_history': order.status_history.all(),
    }
    return render(request, 'orders/track_order.html', context)

def send_order_confirmation_email(order):
    """অর্ডার কনফার্মেশন ইমেইল পাঠানো"""
    subject = f'অর্ডার কনফার্মেশন - #{order.order_number}'
    message = f"""
    প্রিয় {order.full_name},
    
    আপনার অর্ডারটি সফলভাবে প্লেস হয়েছে!
    
    অর্ডার নম্বর: {order.order_number}
    মোট মূল্য: ৳{order.total_amount}
    পেমেন্ট মেথড: {order.get_payment_method_display()}
    
    অর্ডার ট্র্যাক করুন: {settings.SITE_URL}/orders/track/{order.order_number}/
    
    ধন্যবাদ,
    Cactus Shop টিম
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=True,
    )