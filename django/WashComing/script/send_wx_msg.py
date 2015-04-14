# coding=utf-8
import base
import os
import datetime as dt
import logging
import re
import json, base64

from WCBill.models import Bill
from WCLogistics.models import RFD
from WeiXin.models import Fan, WX_API

logger = logging.getLogger('update_shop')
dt_today = dt.date.today()
dt_today = dt.datetime(year=dt_today.year, month=dt_today.month, day=dt_today.day)

# when return order has courier phone, then push wx user the infomation
a_to_return_bills = Bill.objects.filter(status__gt=Bill.WASHING, status__lt=Bill.NEED_FEEDBACK)
for it_bill in a_to_return_bills:
    mo_lg = it_bill.lg
    if None == mo_lg or '' == mo_lg.return_order_no:
        continue
    a_order_res = RFD.GetFetchOrderStation([mo_lg.return_order_no])
    if len(a_order_res) > 0:
        if '' == a_order_res[0]['CellPhone']:
            continue
# detail saved in ext, so no need push
        if 'rfd_return' in it_bill.ext:
            continue
        it_bill.ext['rfd_return'] = a_order_res[0]
        it_bill.save()
# send template message to user to tell him/her courier phone
        re_out = re.search('yz_uid\[(\d+)\]', it_bill.comment)
        if None == re_out:
            continue
        s_yz_uid = re_out.group(1)
        try:
            mo_fan = Fan.objects.get(yz_uid=s_yz_uid)
        except (Exception) as e:
            #todo: get this user from wx
            continue
        s_openid = mo_fan.openid
        d_param = {}
        with open(os.path.join(WX_API.conf_dir, 'weixin.conf'), 'r') as wxconf:
            WX_API.config.readfp(wxconf)
            s_template_get_id = WX_API.config.get('msg', 'template_get_id')
        s_username = base64.b64decode(mo_fan.nickname_b64).decode('utf-8')
        if len(s_username) > 0:
            s_username = u'亲爱的%s，' %(s_username)
        d_rfd_return = it_bill.ext['rfd_return']
        d_param['first'] = {'value': s_username, 'color': '#000000'}
        d_param['keyword1'] = {'value': it_bill.bid, 'color': '#000000'}
        if it_bill.total == it_bill.paid:
            d_param['keyword2'] = {'value': u'已支付', 'color': '#000000'}
        else:
            if it_bill.paid > it_bill.total:
                it_bill.paid = it_bill.total
            d_param['keyword2'] = {'value': u'%.2f元' %(it_bill.total-it_bill.paid), 'color': '#FF0000'}
        s_remark = u'这是为您送衣的物流员电话：%s。如您已在等候，可以召唤他哦~' %(d_rfd_return['CellPhone'])
        d_param['remark'] = {'value': s_remark, 'color': '#000000'}
        js_req = WX_API.send_template_msg(s_openid, s_template_get_id, d_param)
        logging.debug(js_req)
        logging.info('send user get rfd info')


# when get order has courier phone, then push wx user the infomation
a_to_get_bills = Bill.objects.filter(status__gt=Bill.CONFIRMING, status__lt=Bill.WASHING)
for it_bill in a_to_get_bills:
    mo_lg = it_bill.lg
    if None == mo_lg or '' == mo_lg.get_order_no:
        continue
    a_order_res = RFD.GetFetchOrderStation([mo_lg.get_order_no])
    if len(a_order_res) > 0:
        if '' == a_order_res[0]['CellPhone']:
            continue
# detail saved in ext, so no need push
        if 'rfd_get' in it_bill.ext:
            continue
        it_bill.ext['rfd_get'] = a_order_res[0]
        it_bill.save()
# next to send template message to user to tell him/her courier phone
        re_out = re.search('yz_uid\[(\d+)\]', it_bill.comment)
        if None == re_out:
            continue
        s_yz_uid = re_out.group(1)
        try:
            mo_fan = Fan.objects.get(yz_uid=s_yz_uid)
        except (Exception) as e:
            #todo: get this user from wx
            continue
        s_openid = mo_fan.openid
        d_param = {}
        with open(os.path.join(WX_API.conf_dir, 'weixin.conf'), 'r') as wxconf:
            WX_API.config.readfp(wxconf)
            s_template_get_id = WX_API.config.get('msg', 'template_get_id')
        s_username = base64.b64decode(mo_fan.nickname_b64).decode('utf-8')
        if len(s_username) > 0:
            s_username = u'亲爱的%s:' %(s_username)
        d_rfd_get = it_bill.ext['rfd_get']
        d_param['first'] = {'value': s_username, 'color': '#000000'}
        d_param['keyword1'] = {'value': it_bill.bid, 'color': '#000000'}
        if it_bill.total == it_bill.paid:
            d_param['keyword2'] = {'value': u'已支付', 'color': '#000000'}
        else:
            if it_bill.paid > it_bill.total:
                it_bill.paid = it_bill.total
            d_param['keyword2'] = {'value': u'%.2f元（送回结算）' %(it_bill.total-it_bill.paid), 'color': '#FF0000'}
        s_remark = u'为您取衣的物流员电话：%s。如您已在等候，可以召唤他哦~' %(d_rfd_get['CellPhone'])
        d_param['remark'] = {'value': s_remark, 'color': '#000000'}
        js_req = WX_API.send_template_msg(s_openid, s_template_get_id, d_param)
        logging.debug(js_req)
        logging.info('send user get rfd info')

