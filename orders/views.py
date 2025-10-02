import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from shoppingcart import settings
from store.models import Product
from .forms import OrderForm
from carts.models import CartItem
from .models import Order, OrderProduct, Payment
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.


#payment 
@csrf_exempt
def payments(request):
    
    if request.method == "POST":
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        order_number = data.get('order_number')
        try:
            order = Order.objects.get(order_number=order_number, user=request.user)
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Save payment
            payment = Payment.objects.create(
                user=order.user,
                payment_id=razorpay_payment_id,
                payment_method="Razorpay",
                amount_paid=str(order.order_total),  # keep as string if model field is CharField
                status="Completed"
            )

            order.payment = payment
            order.is_ordered = True
            order.status = "Completed"
            order.save()

            #Move the cart item to Order product table 
            cart_items = CartItem.objects.filter(user=request.user)

            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                order_product = OrderProduct.objects.create(
                    order=order,
                    payment=payment,
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    ordered=True
                )
                order_product.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                order_product = OrderProduct.objects.get(id=order_product.id)
                order_product.variations.set(product_variation)
                order_product.save() 




            #reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -=item.quantity
                product.save()



            #clear to the cart 
            CartItem.objects.filter(user=request.user).delete()


            #send order revivced email to user
            order_products = OrderProduct.objects.filter(order=order)

            mail_subject = 'Thank you for your order'
            message = render_to_string('orders/order_recieved_email.html',{
                'user':request.user,
                'order':order,
                'order_products': order_products,
                
               
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            #send order number and transaction id to back to senddata to via json response


            return JsonResponse({
                "status": "success",
                "order_number": order.order_number,
                "razorpay_payment_id": payment.payment_id,
            })

        except Exception as e:
            print("Payment verification failed:", e)
            return JsonResponse({"status": "fail"})

    return JsonResponse({"status": "invalid"})





client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



# def place_order(request,total=0,quantity=0):
#     current_user = request.user
#     #if cart is empty redirect to shop
#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('store')


#     grand_total = 0
#     tax = 0

#     for cart_item in cart_items:
#         total += float(cart_item.product.price * cart_item.quantity)
#         quantity += cart_item.quantity
#     tax = (2 * total)/100
#     grand_total = total + tax

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             #store all the billing information inside Order table
#             data = Order()
#             data.user = current_user
#             data.first_name = form.cleaned_data['first_name']
#             data.last_name = form.cleaned_data['last_name']
#             data.phone = form.cleaned_data['phone']
#             data.email = form.cleaned_data['email']
#             data.address_line_1 = form.cleaned_data['address_line_1']
#             data.address_line_2 = form.cleaned_data['address_line_2']
#             data.country = form.cleaned_data['country']
#             data.state = form.cleaned_data['state']
#             data.city = form.cleaned_data['city']
#             data.order_note = form.cleaned_data['order_note']
#             data.order_total = grand_total
#             data.tax = tax
#             data.ip = request.META.get('REMOTE_ADDR')
#             data.save()

#             #Generate order number
#             yr = int(datetime.date.today().strftime('%Y'))
#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             d = datetime.date(yr,mt,dt)
#             current_date = d.strftime("%Y%m%d")
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()

#             order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
#             context = {
#                 'order':order,
#                 'cart_items': cart_items,
#                 'total':total,
#                 'tax':tax,
#                 'grand_total': grand_total,
#             }


#             return render(request, 'orders/payments.html',context)
#     else:
#         return redirect('checkout')
    




client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If cart is empty redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save order details
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate unique order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # Razorpay order creation (for test mode)
            amount_in_paise = int(grand_total * 100)  # Razorpay works in paise
            razorpay_order = client.order.create(dict(
                amount=amount_in_paise,
                currency='INR',
                payment_capture=1
            ))
            

            # Save Razorpay order_id in session or DB if needed
            request.session['razorpay_order_id'] = razorpay_order['id']
            data.razorpay_order_id = razorpay_order['id']  # Save in order
            data.save()


            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                "amount": int(grand_total * 100),
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')






def order_complete(request):


    return render(request,'orders/order_complete.html')