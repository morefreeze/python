# coding=utf-8
from django.contrib import admin
from WCLib.views import *
from WCBill.models import Bill, Coupon, MyCoupon
from WCLogistics.models import OrderQueue
import datetime as dt

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    pass

class MyCouponAdmin(admin.ModelAdmin):
    pass

def confirm_order(request, id):
    try:
        mo_bill = Bill.objects.get(bid=id)
    except (Bill.DoesNotExist) as e:
        return JSONResponse({'errmsg':'bill not exist [%d]' %(id)})
    if Bill.CONFIRMING == mo_bill.status:
        mo_bill.status = Bill.WAITTING_GET
        mo_bill.add_time(Bill.WAITTING_GET)

        if mo_bill.ext.get('immediate'):
            if None == mo_bill.shop:
                return HttpResponse(u'因为该单为立即下单，请选择一家店铺后再确认订单')
            dt_fetch_time = dt.datetime.now()
            OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.ImportGettingOrders,
                                      status=OrderQueue.TODO, time=dt_fetch_time)
            dt_import_time = mo_bill.return_time_0
            OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.ImportOrders,
                                      status=OrderQueue.TODO, time=dt_import_time)
            mo_bill.save()
            return HttpResponse(u'立即下单成功！请手动返回上一页')
        mo_bill.save()
        return HttpResponse(u'确认订单成功！请手动返回上一页')
    else:
        return HttpResponse(u'订单状态不需要确认 当前状态为 “%s”' %(Bill.get_status(mo_bill.status)))

def show_clothes(request, id):
    try:
        mo_bill = Bill.objects.get(bid=id)
    except (Bill.DoesNotExist) as e:
        return JSONResponse({'errmsg':'bill not exist [%d]' %(id)})
    return render_to_response('admin/WCBill/show_clothes.html', {'clothes':mo_bill.clothes})

class BillAdmin(admin.ModelAdmin):
    buttons = [
        {
             'url': '_confirm',
             'textname': u'确认订单',
             'func': confirm_order,
             'confirm': u'你想确认这个订单吗'
        },
        {
             'url': '_show_clothes',
             'textname': u'展示衣物',
             'func': show_clothes,
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
