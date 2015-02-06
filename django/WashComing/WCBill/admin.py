# coding=utf-8
from django.contrib import admin
from django.contrib import messages
from WCLib.views import *
from WCLib.models import *
from WCBill.models import Bill, Coupon, MyCoupon, Cart, Feedback, \
        Pingpp, Pingpp_Charge, Pingpp_Refund
from WCLogistics.models import OrderQueue
import datetime as dt

# Register your models here.
def parse_clothes(pa_clothes):
    a_clothes = []
    for it_cloth in pa_clothes:
        d_cloth = it_cloth
        if 'price' in it_cloth and 'number' in it_cloth:
            d_cloth['total'] = int(it_cloth['number']) * it_cloth['price']
            #d_cloth[u'总价'] = int(it_cloth['number']) * it_cloth['price']
        a_clothes.append(d_cloth)
    return a_clothes

class CouponAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', 'code', ]

class CartAdmin(admin.ModelAdmin):
    readonly_fields = ['update_time', ]
    def parse_cart(request, id):
        try:
            mo_cart = Cart.objects.get(caid=id)
            t_map = {
                "name": u'名称',
                "image": u'图标',
                "price": u'单价',
                "number": u'数量',
                "cid": u'衣物编号',
            }
            a_clothes = parse_clothes(mo_cart.clothes)
            for it_cloth in a_clothes:
                messages.info(request, u'衣物【%s】 数量【%s】 单价【%.2f】 总价【%.2f】 cid【%d】' \
                    %(it_cloth.get('name'), it_cloth.get('number'), it_cloth.get('price'), \
                     it_cloth.get('total'), it_cloth.get('cid') ) \
                    )
            if 0 == len(a_clothes):
                messages.warning(request, u'暂无衣物信息')
        except (Cart.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    buttons = [
        {
             'url': '_parse_cart',
             'textname': u'解析购物车',
             'func': parse_cart,
        },
    ]

    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['buttons'] = self.buttons
        return super(CartAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(CartAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls

class MyCouponAdmin(admin.ModelAdmin):
    pass

class BillAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', ]

    def confirm_order(request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            if Bill.CONFIRMING == mo_bill.status:
                if mo_bill.ext.get('payment') in ONLINE_PAYMENT and mo_bill.paid < mo_bill.total:
                    messages.error(request, u'这是在线支付订单，需要用户付款后才能确认')
                    return HttpResponseRedirect('..')
                mo_bill.change_status(Bill.WAITTING_GET)

                if mo_bill.ext.get('immediate'):
                    dt_get_time = dt.datetime.now()
                else:
                    dt_get_time = mo_bill.get_time_0
                OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddFetchOrder, \
                                          status=OrderQueue.TODO, time=dt_get_time)
                dt_return_time = mo_bill.return_time_0
                OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder, \
                                          status=OrderQueue.TODO, time=dt_return_time)
                mo_bill.save()
                messages.success(request, u'确认订单成功！')
            else:
                messages.warning(request, u'订单状态不需要确认 当前状态为 “%s”' %(Bill.get_status(mo_bill.status)))
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    def parse_bill(request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            t_map = {
                "name": u'名称',
                "image": u'图标',
                "price": u'单价',
                "number": u'数量',
                "cid": u'衣物编号',
            }
            a_clothes = parse_clothes(mo_bill.clothes)
            for it_cloth in a_clothes:
                messages.info(request, u'衣物【%s】 数量【%s】 单价【%.2f】 总价【%.2f】 cid【%d】' \
                    %(it_cloth.get('name'), it_cloth.get('number'), it_cloth.get('price'), \
                     it_cloth.get('total'), it_cloth.get('cid') ) \
                    )
            if 0 == len(a_clothes):
                messages.warning(request, u'暂无衣物信息')
            messages.info(request, u'总价【%.2f】' %(mo_bill.total))
            i_mcid = mo_bill.ext.get('use_coupon') or 0
            if i_mcid > 0:
                try:
                    mo_mc = MyCoupon.objects.get(mcid=i_mcid)
                    messages.info(request, u'代金券【%s】' %(mo_mc))
                    messages.info(request, u'原价【%.2f】' %(mo_bill.ext['old_total']))
                    messages.info(request, u'价格减免【%.2f】' %(mo_bill.ext.get('price_dst') or 0))
                    messages.info(request, u'折扣减免【%.2f元】' %(mo_bill.ext.get('percent_dst') or 0))
                except (MyCoupon.DoesNotExist) as e:
                    messages.error(request, u'代金券错误【%d】' %(i_mcid))
            else:
                messages.info(request, u'未使用代金券')
            messages.info(request, u'邮费【%.2f】' %(mo_bill.ext.get('shipping_fee') or 0))
            s_payment = mo_bill.ext.get('payment')
            d_pay = {
                'cash' :    u'现金',
                'pos' :     u'POS机',
                'alipay' :  u'支付宝',
                'wx' :      u'微信支付',
                'bfb' :     u'百度钱包',
            }
            if s_payment in d_pay:
                messages.info(request, u'支付方式【%s】' %(d_pay[s_payment]))
            else:
                messages.warning(request, u'支付方式未知')
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    def cancel_bill(request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            if mo_bill.cancel(admin=True):
                messages.success(request, u'订单【%s】取消成功' %(id))
            else:
                messages.error(request, u'订单【%s】取消失败！' %(id))
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    buttons = [
        {
             'url': '_confirm',
             'textname': u'确认订单',
             'func': confirm_order,
             'confirm': u'你想确认这个订单吗'
        },
        {
             'url': '_parse_bill',
             'textname': u'解析订单',
             'func': parse_bill,
        },
        {
             'url': '_cancel_bill',
             'textname': u'强制取消订单',
             'func': cancel_bill,
             'confirm': u'你想取消这个订单吗'
        },
    ]
    def change_view(self, request, object_id, form_url='', extra_context={}):
        mo_bill = Bill.objects.get(bid=object_id)
        if False and mo_bill.status != Bill.CONFIRMING:
            extra_context['buttons'] = [b for b in self.buttons if b['url'] != '_confirm']
        else:
            extra_context['buttons'] = self.buttons
        return super(BillAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(BillAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ['create_time', ]

    buttons = [
    ]

    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['buttons'] = self.buttons
        return super(FeedbackAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(FeedbackAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls


admin.site.register(Coupon,CouponAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(MyCoupon,MyCouponAdmin)
admin.site.register(Bill,BillAdmin)
admin.site.register(Feedback,FeedbackAdmin)
