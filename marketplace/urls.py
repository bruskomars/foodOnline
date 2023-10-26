from django.urls import path
from . import views

urlpatterns=[
    path('', views.marketplace, name='marketplace'),
    path('<vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('add_to_cart/<int:pk>', views.add_to_cart, name='add_to_cart'),
    path('decrease_cart/<int:pk>', views.decrease_cart, name='decrease_cart'),
]