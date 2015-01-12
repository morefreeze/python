from django.contrib import admin
from WCUser.models import User, Shop, Feedback

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ['token', 'third_uids', 'third_token', 'create_time', ]

class ShopAdmin(admin.ModelAdmin):
    pass

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', ]

admin.site.register(User, UserAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Feedback, FeedbackAdmin)
