from django.contrib import admin
from vendor.models import Vendor

# Register your models here.
class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'is_approved', 'created_at',)
    list_display_links = ('user', 'vendor_name',)
    list_editable = ('is_approved',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Vendor, VendorAdmin)