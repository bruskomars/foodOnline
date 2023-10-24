from django.contrib import admin
from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category',)}
    list_display = ('category', 'vendor', 'updated_at')
    search_fields = ('category', 'vendor__vendor_name',)


class FoodItemdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('food_title', 'category', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('food_title', 'category__category', 'vendor__vendor_name', 'price')
    list_filter = ('is_available',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemdmin)
