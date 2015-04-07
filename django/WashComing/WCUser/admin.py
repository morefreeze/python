from django.contrib import admin
from WCUser.models import User, Shop, Feedback

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ['token', 'third_uids', 'third_token', 'create_time', ]
    search_fields = ['name', 'phone', 'email', 'address__real_name']

class ShopAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'own', ]

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', ]

admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Feedback, FeedbackAdmin)
