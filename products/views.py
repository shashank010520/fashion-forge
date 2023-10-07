from django.shortcuts import render
from django.shortcuts import render, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product, Category
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Create your views here.

@login_required
def get_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        return render(request, 'product/product-details.html', context=context)
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)
    except Exception as e:
        print("Error fetching product:", e)
        return HttpResponse("Something went wrong", status=500)



def product_grid(request, cat=None):
    try:
        page = None  # Initialize 'page' variable
        if cat:
            # Perform category lookup based on the category name
            products = Product.objects.filter(category__category_name=cat)
            paginator = Paginator(products, 10)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)
            if not products.exists():
                return HttpResponse("Category not found", status=404)
        else:
            # If 'cat' is not provided, fetch all products
            products = Product.objects.all()
            paginator = Paginator(products, 10)
            page_number = request.GET.get('page')
            page = paginator.get_page(page_number)

        context = {'products': products,'page': page}
        return render(request, 'product/product-grid.html', context=context)
    except Exception as e:
        print("Error fetching category:", e)
        return HttpResponse("Something went wrong", status=500)



    