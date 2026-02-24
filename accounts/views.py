from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, SellerProfile

def register_choice(request):
    return render(request, 'accounts/register_choice.html')

def register_buyer(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone = request.POST['phone']
        address = request.POST['address']
        
        # পাসওয়ার্ড ম্যাচ চেক
        if password != confirm_password:
            messages.error(request, 'পাসওয়ার্ড মিলছে না!')
            return redirect('register_buyer')
        
        # ইউজারনেম ইউনিক কিনা চেক
        if User.objects.filter(username=username).exists():
            messages.error(request, 'এই ইউজারনেম already exists!')
            return redirect('register_buyer')
        
        # ইমেইল ইউনিক কিনা চেক
        if User.objects.filter(email=email).exists():
            messages.error(request, 'এই ইমেইল already registered!')
            return redirect('register_buyer')
        
        # নতুন ইউজার তৈরি
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address,
            user_type='BUYER'
        )
        
        messages.success(request, 'রেজিস্ট্রেশন সফল হয়েছে! এখন লগইন করুন।')
        return redirect('login')
    
    return render(request, 'accounts/register_buyer.html')

def register_seller(request):
    if request.method == 'POST':
        # ইউজার তৈরি
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone = request.POST['phone']
        
        # পাসওয়ার্ড ম্যাচ চেক
        if password != confirm_password:
            messages.error(request, 'পাসওয়ার্ড মিলছে না!')
            return redirect('register_seller')
        
        # ইউজার চেক
        if User.objects.filter(username=username).exists():
            messages.error(request, 'এই ইউজারনেম already exists!')
            return redirect('register_seller')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'এই ইমেইল already registered!')
            return redirect('register_seller')
        
        # ইউজার তৈরি
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            user_type='SELLER',
            is_approved=False
        )
        
        # সেলার প্রোফাইল তৈরি
        SellerProfile.objects.create(
            user=user,
            store_name=request.POST['store_name'],
            store_description=request.POST['store_description'],
            business_address=request.POST['business_address'],
            nid_number=request.POST['nid_number'],
            payment_method=request.POST['payment_method'],
            payment_number=request.POST['payment_number']
        )
        
        messages.success(request, 'আপনার রেজিস্ট্রেশন সফল হয়েছে! অ্যাডমিন অ্যাপ্রুভ করার পর আপনি লগইন করতে পারবেন।')
        return redirect('login')
    
    return render(request, 'accounts/register_seller.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # সেলার অ্যাপ্রুভড কিনা চেক
            if user.user_type == 'SELLER' and not user.is_approved:
                messages.warning(request, 'আপনার অ্যাকাউন্ট এখনও অ্যাপ্রুভ হয়নি। অ্যাডমিন অ্যাপ্রুভ করার পর লগইন করুন।')
                return redirect('login')
            
            login(request, user)
            messages.success(request, f'স্বাগতম {user.username}!')
            
            # ইউজার টাইপ অনুযায়ী রিডাইরেক্ট
            if user.user_type == 'BUYER':
                return redirect('buyer_dashboard')
            elif user.user_type == 'SELLER':
                return redirect('seller_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'ভুল ইউজারনেম বা পাসওয়ার্ড!')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'লগআউট সফল হয়েছে।')
    return redirect('home')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')