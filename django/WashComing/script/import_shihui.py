# coding=utf-8
import os
import django
import sys
import datetime as dt
import hashlib
import urllib, urllib2
import json
import logging

pwd = os.path.dirname(os.path.abspath(__file__))
fa_pwd = os.path.abspath(os.path.join(pwd, '..'))
sys.path.append(fa_pwd)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WashComing.settings")
django.setup()

from WCUser.models import User
from WCBill.models import *

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger('shihui')

s_secret = '3d2546f96aa0e6ddc8b15d747958280e'
s_address_add_url = 'http://api.washcoming.com/address/add'
s_address_del_url = 'http://api.washcoming.com/address/delete'
s_bill_submit_url = 'http://api.washcoming.com/bill/submit'
s_username = u'18612295553'
s_token = 'pbkdf2_sha256$12000$zcYr9nnLd1qi$mOtDAal6pHEBrav28DW+iK4NwyghlMrprOdnAzdT+aY='
with open('last_update_shihui', 'r') as f:
    dt_last = dt.datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S')
dt_now = dt.datetime.now()
dt_tomorrow = dt_now + dt.timedelta(days=0, hours=1)
dt_return = dt_tomorrow + dt.timedelta(days=4)
dt_return1 = dt_return + dt.timedelta(hours=4)
d_cloth_map = {
    u'羽绒服': 33,
    u'羊毛大衣': 31,
    u'棉服': 30,
    u'风衣': 29,
    u'冲锋衣': 11,
}

i_cur_page = 1
try:
    while True:
        d_api_param = {
            'app_id': '63ef9a4fc37047a97b',
            'method': 'kdt.trades.sold.get',
            'timestamp': '%s' %(dt_now.strftime("%Y-%m-%d %H:%M:%S")),
            'v': '1.0',
# method param
            'fields': 'tid,price,buyer_id,buyer_nick,buyer_message,receiver_district,receiver_address,receiver_name,receiver_mobile,total_fee,status,update_time,buyer_nick,orders,coupon_details',
            'status': 'WAIT_SELLER_SEND_GOODS',
            'start_update': '%s' %('2015-03-04 00:50:00'),
            'end_update': '%s' %('2015-03-05 23:50:00'),
            #'start_update': '%s' %(dt_last.strftime("%Y-%m-%d %H:%M:%S")),
            #'end_update': '%s' %(dt_now.strftime("%Y-%m-%d %H:%M:%S")),
            'page_no': i_cur_page,
            'page_size': 50,
        }
        d_sort_param = sorted(d_api_param.iteritems())
        s_md5 = hashlib.md5(s_secret+''.join(['%s%s' %(v[0],v[1]) for v in d_sort_param])+s_secret).hexdigest()
        d_api_param['sign'] = s_md5
        s_url_param = '&'.join(['%s=%s' %(k, v) for k,v in d_api_param.iteritems()])
        s_url = 'http://open.koudaitong.com/api/entry?%s' %(urllib.urlencode(d_api_param))
        #logger.debug(s_url)
        rq_ret = urllib2.urlopen(s_url)
        js_ret = json.loads(rq_ret.read())
        #logger.debug(js_ret)
        for it_bill in js_ret['response']['trades']:
# judge same
            if len(Bill.objects.filter(comment__contains=it_bill['tid'])) > 0:
                continue
            d_address_add = {
                'username': s_username,
                'token':    s_token,
                'real_name':it_bill['receiver_name'],
                'phone':    it_bill['receiver_mobile'],
                'province': u'北京',
                'city':     u'北京市',
                'area':     it_bill['receiver_district'],
                'address':  it_bill['receiver_address'],
                'set_default': False,
            }
            rq_adr_ret = urllib2.urlopen(s_address_add_url, urllib.urlencode(d_address_add))
            js_adr_ret = json.loads(rq_adr_ret.read())
            if 'errno' not in js_adr_ret or int(js_adr_ret['errno']) != 0:
                logger.debug(js_adr_ret)
                raise Exception('address add error %s' %(it_bill['tid']))
            else:
                i_aid = int(js_adr_ret['aid'])
                if False and len(it_bill['orders']) > 1:
                    logger.error('more than 1 cloth %s' %(it_bill['tid']))
                    continue

                a_clothes = []
                for it_order in it_bill['orders']:
                    if it_order['title'] in d_cloth_map:
                        a_clothes.append({"number":it_order['num'], "cid":d_cloth_map[it_order['title']]})
                    else:
                        logger.error('%s not in list %s' %(it_order['title'], it_bill['tid']))
                        a_clothes = []
                        break

                if len(a_clothes) == 0:
                    continue
                else:
                    s_clothes = json.dumps(a_clothes)

                s_coupon = ''
                for it_coupon in it_bill['coupon_details']:
                    if 'PROMOCODE' == it_coupon['coupon_type']:
                        s_coupon = it_coupon['coupon_content']
                if '' != s_coupon:
                    a_mycoupons = MyCoupon.objects.filter(coupon__code=s_coupon, coupon__use_code=True)
                    if len(a_mycoupons) > 0:
                        mo_mycoupon = a_mycoupons[0]
                        d_bill_submit['mcid'] = mo_mycoupon.mcid
                d_bill_submit = {
                    'username': s_username,
                    'token':    s_token,
                    'clothes':  s_clothes,
                    'get_time_0': '%s' %(dt_tomorrow.strftime("%Y-%m-%d %H:%m:%S")),
                    'get_time_1': '%s' %(dt_tomorrow.strftime("%Y-%m-%d %H:%m:%S")),
                    'return_time_0': '%s' %(dt_return.strftime("%Y-%m-%d %H:%m:%S")),
                    'return_time_1': '%s' %(dt_return1.strftime("%Y-%m-%d %H:%m:%S")),
                    'aid':      i_aid,
                    'payment':  'cash',
                    'comment':  u'%s 有赞用户【%s】【%s】%s' %(it_bill['buyer_message'], it_bill['buyer_nick'], it_bill['tid'], s_coupon),
                    'immediate': True,
                }
                logger.debug(d_bill_submit)
                rq_bill_ret = urllib2.urlopen(s_bill_submit_url, urllib.urlencode(d_bill_submit))
                js_bill_ret = json.loads(rq_bill_ret.read())
                logger.debug(js_bill_ret)
                if 'errno' not in js_bill_ret or int(js_bill_ret['errno']) != 0:
                    raise Exception('submit bill error %s %s' %(it_bill['tid'], js_bill_ret))

                d_address_del = {
                    'username': s_username,
                    'token':    s_token,
                    'aid':      i_aid,
                }
                rq_adr_ret = urllib2.urlopen(s_address_del_url, urllib.urlencode(d_address_del))
                js_adr_ret = json.loads(rq_adr_ret.read())
                if 'errno' not in js_adr_ret or int(js_adr_ret['errno']) != 0:
                    raise Exception('address del error %s' %(it_bill['tid']))
            logger.info('%s success' %(it_bill['tid']))

        if len(js_ret['response']['trades']) < 50:
            break
        i_cur_page += 1
except (Exception) as e:
    logger.error('%s' %(e))
    if it_bill != None and 'update_time' in it_bill:
        dt_now = dt.datetime.strptime(it_bill['update_time'], '%Y-%m-%d %H:%M:%S')

with open('last_update_shihui', 'w') as f:
    f.write(dt_now.strftime('%Y-%m-%d %H:%M:%S'))

