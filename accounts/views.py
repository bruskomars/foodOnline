from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode

from vendor.forms import VendorForm
from vendor.models import Vendor

from .forms import *
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .utils import detectUser, send_verification_email
from django.core.exceptions import PermissionDenied

# Restrict user from accessing the unauthorized pages
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


# Create your views here.
def registerUser(request):
    form = UserForm()

    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')

    if request.method == "POST":
        form = UserForm(request.POST)

        if form.is_valid():
            #Create user using the form
            # password = form.cleaned_data['password'] # Way of hashing the password
            # user = form.save(commit=False)
            # user.set_password(password) # Way of hashing the password
            # user.role = User.CUSTOMER
            # user.save()

            # Create user using the create_method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )

            user.role = User.CUSTOMER
            user.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'account_verification_email'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been successfully created')

            return redirect('login')

        else:
            print(form.errors)

    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    form = UserForm()
    v_form = VendorForm()

    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')

    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role = User.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user = user
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'account_verification_email'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Your account has been registered successfully! Please wait for the approval.")
            return redirect('registerVendor')
        else:
            messages.error(request, "Invalid form")

    context = {'form': form, 'v_form': v_form}
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    # Activate the user by setting the is_activate status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account is now activated")

        return redirect('myAccount')

    else:
        messages.error(request, "Invalid activation link")
        return redirect('myAccount')

def loginUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect('myAccount')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('myAccount')

        else:
            messages.error(request, 'Invalid login credentials')

    return render(request, 'accounts/login.html')

def logoutUser(request):
    logout(request)
    messages.info(request, 'You are now logged out')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = 'Reset your password'
            email_template = 'reset_password_email'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, "Reset password link has been sent to your email")
            return redirect('login')

        else:
            messages.error(request, "Account does not exist")  # wrong email
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')

    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if password == password2:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)

            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')

        else:
            messages.error(request, 'Password do not match')
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')