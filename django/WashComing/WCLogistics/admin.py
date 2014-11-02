from django.contrib import admin
from WCLogistics.models import Address

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    pass

admin.site.register(Address, AddressAdmin)
