from django.shortcuts import render
from products.models import Product
from accounts.models import Cart
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    context = {'products' : Product.objects.all()}
    return render(request, 'home/index.html', context)

@login_required
def home(request):
    return render(request, 'home/home.html')

@login_required
def profile(request):
    context = {'orders' : Cart.objects.filter(is_paid = True, user=request.user)}
    return render(request, 'user-components/profile.html', context)

def about(request):
    return render(request, 'user-components/about.html')

def contact(request):
    return render(request, 'user-components/contact.html')
