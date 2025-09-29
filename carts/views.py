from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from .models import Product,Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    
    return cart


# def add_cart(request,product_id):
#     product = Product.objects.get(id=product_id) #get product
#     product_variation = []
#     if request.method == 'POST':
#         # color = request.POST['color']
#         # size = request.POST['size']
#         # print(color,size,"----------------")

#         for item in request.POST:
#             key = item
#             value = request.POST[key]
#             # print(key,value)

#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 print(variation)
#                 product_variation.append(variation)
#             except:
#                 pass
#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart id prenset the session
#     except:
#         if Cart.DoesNotExist:
#             cart = Cart.objects.create(
#                 cart_id = _cart_id(request)
#             )
#     cart.save()


#     is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()

#     if is_cart_item_exists:
#         cart_item = CartItem.objects.filter(product=product, cart=cart)
#         # exisiting_variation -> database
#         #current_variation -> product_variation
#         #item_id -> database
#         ex_val_list = []
#         id = []
#         for item in cart_item:
#             exisiting_variation = item.variations.all()
#             ex_val_list.append(list(exisiting_variation))
#             id.append(item.id)

#             print(ex_val_list)

#         if product_variation in ex_val_list:
#             #incre
#             index = ex_val_list.index(product_variation)
#             item_id = id[index]
#             item.quantity += 1
#             item.save()
            
#         else:
#             if len(product_variation) > 0:
#                 cart_item.variations.clear()
#                 for item in product_variation:
#                     cart_item.variations.add(item) 
            
#             cart_item.save()

#     else:
#         cart_item = CartItem.objects.create(
#         product=product,
#         quantity = 1,
#         cart = cart,
#         )
#         if len(product_variation) > 0:
#             cart_item.variations.clear()

#             for item in product_variation:
#                 cart_item.variations.add(item)    
#         cart_item.save()

#     return redirect('cart')
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # get product
    product_variation = []

    if request.method == 'POST':
        for key, value in request.POST.items():
            # skip csrf token
            if key == 'csrfmiddlewaretoken':
                continue

            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # Get or create cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    # Check if cart item already exists
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_items = CartItem.objects.filter(product=product, cart=cart)

        # existing_variations -> from DB
        # product_variation -> from current request
        ex_val_list = []
        id_list = []

        for item in cart_items:
            existing_variation = item.variations.all()
            ex_val_list.append(list(existing_variation))
            id_list.append(item.id)

        if product_variation in ex_val_list:
            # If same variation exists → increase qty
            index = ex_val_list.index(product_variation)
            item_id = id_list[index]
            cart_item = CartItem.objects.get(id=item_id)
            cart_item.quantity += 1
            cart_item.save()
        else:
            # If variation is new → create new cart item
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if product_variation:
                cart_item.variations.set(product_variation)
            cart_item.save()
    else:
        # If no cart item exists → create new
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        if product_variation:
            cart_item.variations.set(product_variation)
        cart_item.save()

    return redirect('cart')




def remove_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    print(cart,"=================")
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0,quantity=0 ,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)

        tax = (2 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'qunatity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
             
    return render(request,'store/cart.html',context)