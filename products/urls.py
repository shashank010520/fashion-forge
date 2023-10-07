from django.urls import path
from products.views import *

urlpatterns = [
    path('product-grid/', product_grid, name='product_grid'),
        # URL pattern for products based on categories
    path('product-grid/<cat>/',product_grid, name='category_products'),
    path('<slug>/', get_product, name='get_product'),
]