from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from .context_processors import get_cart_counter
from .models import Cart
from menu.models import Category, FoodItem
from vendor.models import Vendor


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(user__is_active=True, is_approved=True)
    vendor_count = vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # formerly request.is_ajax()
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=pk)
                # check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
                except:
                    chkCart = Cart.objects.create(
                        user=request.user,
                        fooditem=fooditem,
                        quantity=1,
                    )
                    return JsonResponse({'status': 'Success', 'message': 'Food item added to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity })

            except:
                JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})

        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})

    return JsonResponse({'status': 'login_required', 'message': 'Please log in to continue'})

def decrease_cart(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # formerly request.is_ajax()
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=pk)
                chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)

                # Decrease the cart quantity
                if chkCart.quantity >= 1:
                    chkCart.quantity -= 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Decrease quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})

                else:
                    return JsonResponse(
                        {'status': 'Failed', 'message': 'You do not have this item in the cart', 'cart_counter': get_cart_counter(request)})

            except:
                JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})

        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})

    return JsonResponse({'status': 'Failed', 'message': 'Please log in to continue'})