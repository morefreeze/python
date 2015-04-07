# coding=utf-8
import os
import django
import sys
import datetime as dt
import hashlib
import urllib, urllib2
import json
import logging
import re

pwd = os.path.dirname(os.path.abspath(__file__))
fa_pwd = os.path.abspath(os.path.join(pwd, '..'))
sys.path.append(fa_pwd)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WashComing.settings")
django.setup()

from WCUser.models import User
from WCBill.models import *
from WCLib.models import *
from WCCloth.models import *

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
# prevent some user from missing
    dt_last -= dt.timedelta(hours=16)
dt_now = dt.datetime.now()
dt_tomorrow = dt_now + dt.timedelta(days=0, hours=1)
dt_return = dt_tomorrow + dt.timedelta(days=4)
dt_return1 = dt_return + dt.timedelta(hours=4)
def make_all_cloth_map():
    d_ret = {}
    a_clothes = Cloth.objects.filter(is_leaf=True)
    for it_cloth in a_clothes:
        try:
            mo_fa_cid = it_cloth.fa_cid
            if None == mo_fa_cid.fa_cid:
                mo_fa_cid = None
        except (Exception) as e:
# some cloth father is not exist e.g. cid=81
            continue
        s_name = ''
        i_cid = int(it_cloth.cid)
        if None != mo_fa_cid:
            s_name = "%s（%s）" %(mo_fa_cid.name, it_cloth.name)
        else:
            s_name = "%s" %(it_cloth.name)
        d_ret[s_name] = i_cid
    return d_ret

d_all_map = make_all_cloth_map()

d_cloth_map = {
    '216351': d_all_map,
    '217943': d_all_map,
    '217947': d_all_map,
    '235144': d_all_map,
    '235143': d_all_map,
    '235141': d_all_map,
    '235140': d_all_map,
    '234515': d_all_map,
    'all':      d_all_map,
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
            'fields': 'tid,price,buyer_id,buyer_nick,buyer_message,receiver_district,receiver_address,receiver_name,receiver_mobile,total_fee,payment,status,update_time,buyer_nick,orders,coupon_details',
            'status': 'WAIT_SELLER_SEND_GOODS',
            #'start_update': '%s' %('2015-03-05 12:50:00'),
            #'end_update': '%s' %('2015-03-05 18:50:00'),
            'start_update': '%s' %(dt_last.strftime("%Y-%m-%d %H:%M:%S")),
            'end_update': '%s' %(dt_now.strftime("%Y-%m-%d %H:%M:%S")),
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
            it_bill['buyer_nick'] = re.sub(ur'[^\u4e00-\u9fa5\w]', '', it_bill['buyer_nick'])
            b_find_area = False
            for it_area in Area_Choice:
                if it_area[0] in it_bill['receiver_address']:
                    it_bill['receiver_district'] = it_area[0]
                    b_find_area = True
                if it_area[0] == it_bill['receiver_district']:
                    b_find_area = True
            if not b_find_area or u'北京市' == it_bill['receiver_district']:
                logger.error('area not exist %s' %(it_bill['tid']))
                it_bill['receiver_district'] = u'西城区'
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

                s_coupon = ''
                s_coupon_id = ''
                for it_coupon in it_bill['coupon_details']:
                    if 'PROMOCODE' == it_coupon['coupon_type']:
                        s_coupon = it_coupon['coupon_content']
                        s_coupon_id = it_coupon['coupon_id']

                if '' == s_coupon_id:
                    s_coupon_id = 'all'
                    logger.debug('this bill may use shihui code not coupon %s' %(it_bill['tid']))

                if s_coupon_id not in d_cloth_map:
                    logger.error('%s not in mycoupon %s' %(s_coupon_id, it_bill['tid']))
                    continue

                a_clothes = []
                for it_order in it_bill['orders']:
                    if it_order['title'] in d_cloth_map[s_coupon_id]:
                        a_clothes.append({"number":it_order['num'], "cid":d_cloth_map[s_coupon_id][it_order['title']]})
                    else:
                        logger.error('%s not in list %s' %(it_order['title'], it_bill['tid']))
                        a_clothes = []
                        break

                if len(a_clothes) == 0:
                    continue
                else:
                    s_clothes = json.dumps(a_clothes)

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
                if '' != s_coupon:
                    a_mycoupons = MyCoupon.objects.filter(coupon__code=s_coupon, coupon__use_code=True)
                    if len(a_mycoupons) > 0:
                        mo_mycoupon = a_mycoupons[0]
                        d_bill_submit['mcid'] = mo_mycoupon.mcid
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
                if 'bid' in js_adr_ret:
                    mo_bill = Bill.objects.get(bid=js_adr_ret['bid'])
                    mo_bill.payment = it_bill['payment']
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

