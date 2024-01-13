from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify

from django.db import IntegrityError

from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem
from orders.models import Order, OrderedFood

from vendor.forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm

from vendor.models import Vendor, OpeningHour


# Create your views here.

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated.")
            return redirect('vprofile')

        else:
            messages.error(request, "Invalid input")

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')

    context = {
        'categories':categories,
    }

    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)

    context = {
        'fooditems':fooditems,
        'category':category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)


#################### CATEGORY CRUD #######################
#################### CATEGORY CRUD #######################
#################### CATEGORY CRUD #######################
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat_name = form.cleaned_data['category'] # for slug field
            category = form.save(commit=False)

            category.vendor = get_vendor(request)
            category.save() # to generate the cat slug id

            category.slug = slugify(cat_name)+"-"+str(+category.id)
            category.save()

            messages.success(request, 'New category added successfully!')
            return redirect('menu-builder')



    context = {
        'form':form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            cat_name = form.cleaned_data['category'] # for slug field
            category = form.save(commit=False)

            category.vendor = get_vendor(request)
            category.slug = slugify(cat_name)
            category.save()

            messages.success(request, 'Category updated successfully!')
            return redirect('menu-builder')

    context = {
        'form':form,
        'category':category,
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()

    messages.success(request, "Category has been deleted successfully")
    return redirect('menu-builder')

#################### FOOD ITEM CRUD #######################
#################### FOOD ITEM CRUD #######################
#################### FOOD ITEM CRUD #######################

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    form = FoodItemForm()
    # modify this form so that the options in form for categories is restricted to specific vendor
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']  # for slug field
            food = form.save(commit=False)

            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()

            messages.success(request, 'New food item added successfully!')
            return redirect('fooditems_by_category', food.category.id)

    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk):
    food = get_object_or_404(FoodItem, pk=pk)
    form = FoodItemForm(instance=food)
    form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']  # for slug field
            food = form.save(commit=False)

            food.vendor = get_vendor(request)
            food.slug = slugify(food_title)
            food.save()

            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)

    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()

    messages.success(request, "Food Item has been deleted successfully")
    return redirect('fooditems_by_category', food.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()

    context = {
        'form': form,
        'opening_hours': opening_hours,

    }
    return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    # handle the data from ajax request
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # formerly request.is_ajax()

            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHour.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed,
                )

                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'Success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'Success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour , 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                return JsonResponse({'status': 'Failed', 'message': from_hour+'-'+to_hour+' already exists for this day!', 'error': str(e)})
        else:
            HttpResponse('Invalid request')

def remove_opening_hours(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # formerly request.is_ajax()
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'Success', 'id': pk})

def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))

        context = {
            'ordered_food': ordered_food,
            'order': order,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }

        return render(request, 'vendor/order_detail.html', context)

    except:
        return redirect('vendor')

def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/my_orders.html', context)