from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.contrib import messages

# Create your views here.
def registerUser(request):
    form = UserForm()

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
            messages.success(request, 'Your account has been successfully created')

            return redirect('registerUser')

        else:
            print(form.errors)

    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)