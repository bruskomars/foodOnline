from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order
import simplejson as json
from .utils import generate_order_number

# Create your views here.
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    # Get value from context_processor
    subtotal = get_cart_amounts(request)['subtotal']
    grandtotal = get_cart_amounts(request)['grand_total']
    total_tax = get_cart_amounts(request)['tax']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grandtotal
            order.tax_data = json.dumps(tax_data) # convert data from database to json
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method'] ## Get the payment method in checkout URL

            order.save() #order.id is generated

            order.order_number = generate_order_number(order.id)
            order.save()

            return redirect('place_order')

        else:
            print(form.errors) # check error in forms

    return render(request, 'orders/place_order.html')