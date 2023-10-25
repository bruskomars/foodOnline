from django.urls import path
from . import views

urlpatterns=[
    path('', views.marketplace, name='marketplace'),
    path('<vendor_slug>/', views.vendor_detail, name='vendor_detail'),
]