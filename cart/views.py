from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .models import Cart, CartItem

def get_or_create_cart(request):
    """ইউজারের কার্ট পাওয়া বা তৈরি করা"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return None

@login_required
def cart_detail(request):
    """কার্টের বিস্তারিত দেখানো"""
    cart = get_or_create_cart(request)
    
    if cart and cart.items.exists():
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related('product').all(),
            'subtotal': cart.subtotal,
            'shipping_cost': cart.shipping_cost,
            'total': cart.total,
        }
    else:
        context = {
            'cart': cart,
            'cart_items': [],
            'subtotal': 0,
            'shipping_cost': 0,
            'total': 0,
        }
    
    return render(request, 'cart/cart_detail.html', context)

@login_required
@require_POST
def cart_add(request, product_id):
    """কার্টে পণ্য যোগ করা"""
    product = get_object_or_404(Product, id=product_id, available=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # স্টক চেক
    if quantity > product.stock:
        messages.error(request, f'দুঃখিত! শুধু {product.stock}টি পণ্য স্টকে আছে।')
        return redirect('product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # আগে থেকে থাকলে পরিমাণ বাড়ান
        new_quantity = cart_item.quantity + quantity
        if new_quantity <= product.stock:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'{product.name} এর পরিমাণ বাড়ানো হয়েছে!')
        else:
            messages.error(request, f'দুঃখিত! শুধু {product.stock}টি পণ্য স্টকে আছে।')
            return redirect('cart_detail')
    else:
        messages.success(request, f'{product.name} কার্টে যোগ করা হয়েছে!')
    
    return redirect('cart_detail')

@login_required
@require_POST
def cart_update(request, product_id):
    """কার্টে পণ্যের পরিমাণ আপডেট"""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(request, f'দুঃখিত! শুধু {product.stock}টি পণ্য স্টকে আছে।')
        return redirect('cart_detail')
    
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'{product.name} এর পরিমাণ আপডেট করা হয়েছে!')
    else:
        cart_item.delete()
        messages.success(request, f'{product.name} কার্ট থেকে সরানো হয়েছে!')
    
    return redirect('cart_detail')

@login_required
def cart_remove(request, product_id):
    """কার্ট থেকে পণ্য সরানো"""
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        messages.success(request, f'{product.name} কার্ট থেকে সরানো হয়েছে!')
    except CartItem.DoesNotExist:
        messages.error(request, 'পণ্যটি কার্টে নেই!')
    
    return redirect('cart_detail')

@login_required
def cart_clear(request):
    """সম্পূর্ণ কার্ট খালি করা"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'আপনার কার্ট খালি করা হয়েছে!')
    return redirect('cart_detail')