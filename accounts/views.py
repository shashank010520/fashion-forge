from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from products.models import *
from accounts.models import Cart, CartItems
from .models import Profile
import razorpay
from .forms import ProductSearchForm
import pprint
from random import shuffle
# Create your views here.

def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/home')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/home')
    except Exception as e:
        return HttpResponse('Invalid Email token')

def remove_cart(request, cart_item_uid):
    try:
        cart_item =  CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def cart(request):
    cart = None
    cart_total = None
    random_products = []

    try:
        cart = Cart.objects.filter(is_paid=False, user=request.user).first()
        cart_total = cart.get_cart_total()
        products = list(Product.objects.all())  # Convert QuerySet to a list
        shuffle(products)
        random_products = products[:10]
    except Exception as e:
        print(e)

    context = {
        'cart': cart,
        'cart_total': cart_total,
        'random_products': random_products,
    }
    return render(request, 'user-components/cart.html', context)

def product_search(request):
    base_template = 'base/home-base.html'  # If authenticated
    if not request.user.is_authenticated:
        base_template = 'base/base.html'  # If not authenticated

    form = ProductSearchForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            # Use 'product_name' instead of 'name' in the filter
            products = products.filter(product_name__icontains=query)

    context = {
        'base_template': base_template,
        'form': form,
        'products': products,
    }

    return render(request, 'user-components/search.html', context)


@login_required
def checkout(request):
    cart = Cart.objects.filter(is_paid=False, user=request.user).first()
    cart_total = cart.get_cart_total()
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        profile.phone_number = request.POST.get('phone_number')  
        profile.address = request.POST.get('address') 
        profile.landmark = request.POST.get('landmark') 
        profile.city = request.POST.get('city') 
        profile.country = request.POST.get('country')
        profile.pin_code = request.POST.get('pin_code') 
        profile.save()
        return redirect('payment')
    context = {'profile':profile,
               'cart':cart,
               'cart_total':cart_total
               }
    return render(request, 'checkout/checkout.html',context)


from django.conf import settings
@login_required
def checkout_next(request):
    cart = None
    cart_total = None
    razorpay_total = None
    profile = None
    payment = None
    try:
        cart = Cart.objects.filter(is_paid=False, user=request.user).first()
        cart_total = cart.get_cart_total()
        razorpay_total = cart.get_cart_total() * 100
        profile = Profile.objects.get(user=request.user)
    except Exception as e:
        print(e)

    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon).first()

        if not coupon_obj:
            messages.warning(request, 'Invalid Coupon!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart.coupon:
            messages.warning(request, 'Coupon already exists!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_total < coupon_obj.minimum_amount:
            messages.warning(request, f'Minimum amount should be greater than {coupon_obj.minimum_amount}.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if coupon_obj.is_expired:
            messages.warning(request, 'Coupon has been expired!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart.coupon = coupon_obj
        cart.save()

        messages.success(request, 'Coupon Applied')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    if cart:
        client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
        try:
            payment = client.order.create({'amount': cart.get_cart_total() * 100, 'currency': 'INR', 'payment_capture': 1})
            print('*******')
            print(payment)
            print('*******')
            cart.razor_pay_order_id = payment['id']
            cart.save()
        except Exception as e:
            print('Error creating Razorpay order:', e)
            # Handle the error appropriately, for example, redirect the user to an error page.
    context = {
        'cart': cart,
        'cart_total': cart_total,
        'payment': payment,
        'razorpay_total' : razorpay_total,
        'profile' : profile,
    }
    return render(request, 'checkout/checkout-next.html', context)


def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    
    product = Product.objects.get(uid=uid)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_item = CartItems.objects.create(cart=cart, product=product)
    
    
    if variant:
          variant = request.GET.get('variant')
          size_variant = SizeVariant.objects.get(size_name = variant)
          cart_item.size_variant = size_variant
          cart_item.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid= cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def success(request):
    profile = Profile.objects.get(user=request.user)
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razor_pay_order_id = order_id)
    cart.is_paid = True
    cart.order_price = cart.get_cart_total()
    cart.save()
    context = {'profile': profile,
               'cart': cart
               }
    return render(request,'checkout/success.html',context)
    
    