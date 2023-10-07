from accounts.models import Cart
from products.models import *
from django.contrib.auth import get_user

def cart_context_processor(request):
    user = get_user(request)
    if user.is_authenticated:
        cart = Cart.objects.filter(is_paid=False, user=user).first()
        product = Product.objects.all()
        category = Category.objects.all()
        return {'cart': cart,
                'products':product,
                'category':category
                }
    else:
        return {}