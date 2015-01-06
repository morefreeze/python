# coding=utf-8
from django.contrib import admin
from WCLib.views import *
from WCBill.models import Bill, Coupon, MyCoupon, Cart
from WCLogistics.models import OrderQueue
import datetime as dt

# Register your models here.
class CouponAdmin(admin.ModelAdmin):
    pass

class CartAdmin(admin.ModelAdmin):
    pass

class MyCouponAdmin(admin.ModelAdmin):
    pass

class BillAdmin(admin.ModelAdmin):
    def confirm_order(request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
        except (Bill.DoesNotExist) as e:
            return JSONResponse({'errmsg':'bill not exist [%d]' %(id)})
        if Bill.CONFIRMING == mo_bill.status:
            mo_bill.change_status(Bill.WAITTING_GET)

            dt_get_time = dt.datetime.now()
            OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddFetchOrder, \
                                      status=OrderQueue.TODO, time=dt_get_time)
            dt_return_time = mo_bill.return_time_0
            OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder, \
                                      status=OrderQueue.TODO, time=dt_return_time)
            mo_bill.save()
            return HttpResponse(u'确认订单成功！请手动返回上一页')
        else:
            return HttpResponse(u'订单状态不需要确认 当前状态为 “%s”' %(Bill.get_status(mo_bill.status)))

    def show_clothes(request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            t_map = {
                "name": u'名称',
                "image": u'图标',
                "price": u'单价',
                "number": u'数量',
                "cid": u'衣物编号',
            }
            a_clothes = []
            for it_cloth in mo_bill.clothes:
                d_cloth = {}
                for k,v in t_map.items():
                    if k in it_cloth:
                        d_cloth[v] = it_cloth[k]
                if 'price' in it_cloth and 'number' in it_cloth:
                    d_cloth[u'总价'] = int(it_cloth['number']) * it_cloth['price']
                a_clothes.append(d_cloth)
        except (Bill.DoesNotExist) as e:
            return JSONResponse({'errmsg':'bill not exist [%d]' %(id)})
        return render_to_response('admin/WCBill/show_clothes.html', {'clothes':a_clothes})

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
        mo_bill = Bill.objects.get(bid=object_id)
        if mo_bill.status != Bill.CONFIRMING:
            extra_context['buttons'] = [b for b in self.buttons if b['url'] != '_confirm']
        else:
            extra_context['buttons'] = self.buttons
        return super(BillAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(BillAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls

admin.site.register(Coupon,CouponAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(MyCoupon,MyCouponAdmin)
admin.site.register(Bill,BillAdmin)
