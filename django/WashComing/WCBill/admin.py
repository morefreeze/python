# coding=utf-8
from django.contrib import admin
from WCBill.models import Bill, Coupon, MyCoupon

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    pass

class MyCouponAdmin(admin.ModelAdmin):
    pass

def add_logistics_order(request, id):
    pass

class BillAdmin(admin.ModelAdmin):
    buttons = [
        {
            'url': '_ban_action',
             'textname': 'Ban user',
             'func': add_logistics_order,
             'confirm': u'Do you want ban this user?'
        },
    ]
    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['buttons'] = self.buttons
        return super(BillAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(BillAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls

admin.site.register(Coupon,CouponAdmin)
admin.site.register(MyCoupon,MyCouponAdmin)
admin.site.register(Bill,BillAdmin)
