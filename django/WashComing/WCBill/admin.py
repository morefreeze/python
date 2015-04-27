# coding=utf-8
from django.contrib import admin
from django.contrib import messages
from WCLib.views import *
from WCLib.models import *
from WCBill.models import Bill, Coupon, MyCoupon, Cart, Feedback, \
        Pingpp, Pingpp_Charge, Pingpp_Refund
from WCLogistics.models import OrderQueue, RFD
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
    search_fields = ['coupon__code', 'coupon__name', 'own__name',]

class BillAdmin(admin.ModelAdmin):

    def confirm_order(self, request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            if Bill.CONFIRMING == mo_bill.status:
                if mo_bill.ext.get('payment') in ONLINE_PAYMENT and mo_bill.paid < mo_bill.total:
                    messages.error(request, u'这是在线支付订单【%s】，需要用户付款后才能确认' %(id))
                    return HttpResponseRedirect('..')
                mo_bill.change_status(Bill.WAITTING_GET)

                if mo_bill.ext.get('immediate'):
                    dt_get_time = dt.datetime.now()
                else:
                    dt_get_time = mo_bill.get_time_0
                # mark origin order done
                OrderQueue.objects.filter(bill=mo_bill, status__lt=OrderQueue.NO_DO_BUT_DONE).update(status=OrderQueue.NO_DO_BUT_DONE)
                OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddFetchOrder, \
                                          status=OrderQueue.TODO, time=dt_get_time)
                dt_return_time = mo_bill.return_time_0
                #OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder, \
                #                          status=OrderQueue.TODO, time=dt_return_time)
                mo_bill.save()
                messages.success(request, u'确认订单【%s】成功！' %(id))
            else:
                messages.warning(request, u'订单【%s】状态不需要确认 当前状态为 “%s”' %(id, Bill.get_status(mo_bill.status)))
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    def parse_bill(self, request, id):
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

    def cancel_bill(self, request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            if mo_bill.cancel(admin=True):
                messages.success(request, u'订单【%s】取消成功' %(id))
            else:
                messages.error(request, u'订单【%s】取消失败！' %(id))
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')

    def get_fetch_order_station(self, request, id):
        try:
            mo_bill = Bill.objects.get(bid=id)
            mo_lg = mo_bill.lg
            if None != mo_lg:
                a_get_order = RFD.GetFetchOrderStation([mo_lg.get_order_no, mo_lg.return_order_no])
                t_map = {
                    'CellPhone':    u'电话',
                    'FetchMan':     u'配送员',
                    'DistributionName': u'分配站点',
                    'FetchOrderNo':     u'受理单号',
                    'FetchStatus':      u'分配状态',
                    'AssignTime':       u'分配时间',
                }
                for it_get_order in a_get_order:
                    for k,v in t_map.iteritems():
                        if k in it_get_order:
                            messages.info(request, '%s: %s' %(v, it_get_order[k]))
                    if it_get_order.get('FetchOrderNo') == mo_lg.get_order_no:
                        messages.info(request, '%s: %s' %(u'取送类型', u'取衣单'))
                    if it_get_order.get('FetchOrderNo') == mo_lg.return_order_no:
                        messages.info(request, '%s: %s' %(u'取送类型', u'送衣单'))
                    messages.warning(request, '-'*50)
                if len(a_get_order) == 0:
                    messages.warning(request, u'无物流消息或尚未更新，请稍后重试')
                else:
                    pass
            else:
                messages.warning(request, u'无物流消息或尚未更新，请稍后重试')
        except (Bill.DoesNotExist) as e:
            messages.error(request, u'订单号【%s】不存在！' %(id))
        return HttpResponseRedirect('..')
# button func end

    def batch_confirm(self, request, queryset):
        for obj in queryset:
            self.confirm_order(request, obj.pk)
    batch_confirm.short_description = u'批量确认订单（可以全选）'

    def __init__(self, *args, **kwargs):
        self.buttons = [
            {
                 'url': '_confirm',
                 'textname': u'确认订单',
                 'func': self.confirm_order,
                 'confirm': u'你想确认这个订单吗'
            },
            {
                 'url': '_parse_bill',
                 'textname': u'解析订单',
                 'func': self.parse_bill,
            },
            {
                 'url': '_cancel_bill',
                 'textname': u'强制取消订单',
                 'func': self.cancel_bill,
                 'confirm': u'你想取消这个订单吗'
            },
            {
                 'url': '_get_order_station',
                 'textname': u'查询物流分配情况',
                 'func': self.get_fetch_order_station,
            },
        ]
        super(BillAdmin, self).__init__(*args, **kwargs)

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

    def lg_rfd(self, obj):
        from django.core import urlresolvers
        url = urlresolvers.reverse("admin:WCLogistics_rfd_changelist")
        text = u"查看物流"
        if obj.lg:
            return u"<a href='%s%d'>%s</a>" %(url, obj.lg.pk, text)
        else:
            return u"暂无物流信息"
    lg_rfd.allow_tags = True

    readonly_fields = ['create_time', ]
    actions = [batch_confirm, ]
    list_filter = ('status', )
    search_fields = ['real_name', 'address', 'phone', 'bid', 'comment', 'lg__get_order_no', 'lg__return_order_no', ]
    list_display = ['__unicode__', 'lg_rfd', ]

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

from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    #readonly_fields = LogEntry._meta.get_all_field_names()

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]


    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'
    
    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


admin.site.register(LogEntry, LogEntryAdmin)
