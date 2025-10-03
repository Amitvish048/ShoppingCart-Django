from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render,HttpResponse

from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from .models import Product, ReviewRating
from carts.views import _cart_id,CartItem
from django.core.paginator import  EmptyPage,PageNotAnInteger, Paginator 
from django.db.models import Q
# Create your views here.




def store(request, category_slug=None):
    category = None
    products = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
        products_count = products.count()
        paginator = Paginator(products, 4)
        page  = request.GET.get('page')
        paged_products = paginator.get_page(page)

    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 4)
        page  = request.GET.get('page')
        paged_products = paginator.get_page(page)

        products_count = products.count()


    return render(request, 'store/store.html', {
        'products': paged_products, 
        'category': category,
        'products_count':products_count
    })


def product_detail(request, category_slug, product_slug):
    try:
        single_product= Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    
    try:
        if request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        else:
            orderproduct = None
    
    except OrderProduct.DoesNotExist:
        orderproduct = None
    
    #get star review
    reviews = ReviewRating.objects.filter(product_id = single_product.id,status=True)



    context = {

            'single_product': single_product,
            'in_cart'       : in_cart,
            'orderproduct' : orderproduct,
            'reviews': reviews,
        } 
    return render(request,'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | (Q(product_name__icontains=keyword)))
            products_count = products.count()

    context = {
        'products':products,
        'products_count':products_count,
    }
    return render (request,'store/store.html',context)


def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted')

                return redirect(url)

            