# coding=utf-8
from django.contrib import admin
from WCBill.models import Bill, Coupon

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    pass

class BillAdmin(admin.ModelAdmin):
    pass
admin.site.register(Coupon,CouponAdmin)
admin.site.register(Bill,BillAdmin)
