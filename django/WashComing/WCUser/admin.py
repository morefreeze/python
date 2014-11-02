from django.contrib import admin
from WCUser.models import User, Shop

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    pass

class ShopAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
