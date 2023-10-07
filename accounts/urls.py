from django.urls import path
from accounts.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
   path('login/' , login_page , name="login" ),
   path('register/' , register_page , name="register"),
   path('activate/<email_token>/', activate_email, name="activate_email"),
   path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   path('cart/' , cart, name="cart"),
   path('checkout/' , checkout, name="checkout"),
   path('payment/' , checkout_next, name="payment"),
   path('add-to-cart/<uid>/' , add_to_cart, name="add_to_cart"),
   path("remove-cart/<cart_item_uid>/", remove_cart, name="remove_cart"),
   path("remove-coupon/<cart_id>/", remove_coupon, name="remove_coupon"),
   path('success/', success, name="success"),
   path('search/', product_search, name='product_search'),
   
]