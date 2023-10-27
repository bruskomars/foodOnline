from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from .context_processors import get_cart_counter, get_cart_amounts
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
                    return JsonResponse({'status': 'Success', 'message': 'Increased quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(
                        user=request.user,
                        fooditem=fooditem,
                        quantity=1,
                    )
                    return JsonResponse({'status': 'Success', 'message': 'Food item added to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)})

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
                    return JsonResponse({'status': 'Success', 'message': 'Decrease quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount':get_cart_amounts(request)})

                else:
                    return JsonResponse(
                        {'status': 'Failed', 'message': 'You do not have this item in the cart'})

            except:
                JsonResponse({'status': 'Failed', 'message': 'This food does not exist'})

        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})

    return JsonResponse({'status': 'Failed', 'message': 'Please log in to continue'})

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')

    context={'cart_items':cart_items}
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # formerly request.is_ajax()
            try:
                # check if cart item exists
                cart_item = Cart.objects.get(user=request.user, id=pk)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item successfully deleted', 'cart_counter': get_cart_counter(request), 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart item does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})

def search(request):
    keyword = request.GET['keyword']
    address = request.GET['address']
    latitude = request.GET['lat']
    longitude = request.GET['lng']
    radius = request.GET['radius']

    fetch_vendors_by_fooditem = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)

    vendors = Vendor.objects.filter(
        Q(id__in=fetch_vendors_by_fooditem) |
        Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
    )
    vendor_count = vendors.count()

    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)