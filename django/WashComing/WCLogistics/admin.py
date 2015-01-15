# coding=utf-8
from django.contrib import admin
from django.contrib import messages
from WCLib.serializers import *
from WCLib.views import *
from WCLogistics.models import Address, RFD
import datetime as dt

# Register your models here.
class AddressAdmin(admin.ModelAdmin):
    pass

def format_way(d_way):
    dt_ot = dt.datetime.strptime(d_way['OperateTime'], '%Y%m%d%H%M%S')
    s_ret = ''
    s_ret += u'【%s】' %(dt_ot.strftime(FULL_DATETIME_FORMAT))
    s_ret += u'【操作id %s】' %(d_way['OperateId'])
    s_ret += u'【运单号%s】' %(d_way['WaybillNo'])
    s_ret += u'【受理单号%s】' %(d_way['CustomerOrder'])
    s_ret += u'【信息%s】' %(d_way['Result'])
    return s_ret

class RFDAdmin(admin.ModelAdmin):
    def parse_ext(request, id):
        try:
            mo_rfd = RFD.objects.get(lid=id)
            if 0 == len(mo_rfd.ext):
                messages.warning(request, u'暂无物流信息')
# sort ext by OperateId
            d_sort_time = {}
            for it_way in mo_rfd.ext:
                d_sort_time[ it_way['OperateId'] ] = it_way['OperateTime']
            l_sort_time = sorted(d_sort_time.items(), key=lambda e:e[0])
            for s_OperateId, s_OperateTime in l_sort_time:
                for it_way in mo_rfd.ext:
                    if it_way['OperateId'] == s_OperateId and it_way['OperateTime'] == s_OperateTime:
                        messages.info(request, format_way(it_way))
        except (RFD.DoesNotExist) as e:
            messages.error(request, u'物流号【%d】不存在！' %(id))
        return HttpResponseRedirect('..')

    buttons = [
        {
            'url': '_parse_ext',
            'textname': u'解析物流订单',
            'func': parse_ext,
        },
    ]

    def change_view(self, request, object_id, form_url='', extra_context={}):
        extra_context['buttons'] = self.buttons
        return super(RFDAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        from django.conf.urls import patterns, url, include
        urls = super(RFDAdmin, self).get_urls()
        my_urls = list( (url(r'^(.+)/%(url)s/$' % b, self.admin_site.admin_view(b['func'])) for b in self.buttons) )
        return my_urls + urls

admin.site.register(Address, AddressAdmin)
admin.site.register(RFD, RFDAdmin)
