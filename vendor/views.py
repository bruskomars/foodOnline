from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify

from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, FoodItem

from vendor.forms import VendorForm
from accounts.forms import UserProfileForm

from vendor.models import Vendor

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

    print(fooditems)
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


