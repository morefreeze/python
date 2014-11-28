from django.contrib import admin
from WCApp.models import Android

# Register your models here.
class AndroidAdmin(admin.ModelAdmin):
    pass

admin.site.register(Android, AndroidAdmin)
