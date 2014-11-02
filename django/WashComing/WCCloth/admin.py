from django.contrib import admin
from WCCloth.models import Cloth

# Register your models here.
class ClothAdmin(admin.ModelAdmin):
    pass

admin.site.register(Cloth, ClothAdmin)
