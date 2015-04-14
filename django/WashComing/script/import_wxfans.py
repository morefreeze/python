# coding=utf-8
import os
import django
import sys
import base64, hashlib
import datetime as dt
import urllib, urllib2
import json
import logging

pwd = os.path.dirname(os.path.abspath(__file__))
fa_pwd = os.path.abspath(os.path.join(pwd, '..'))
sys.path.append(fa_pwd)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WashComing.settings")
django.setup()

from WeiXin.models import *

a_db_fans = Fan.objects.all()
i_len_dbfans = len(a_db_fans)
a_fans = WX_API.get_users()
i_len_fans = len(a_fans)

s_secret = '3d2546f96aa0e6ddc8b15d747958280e'

cnt = 0
for s_openid in a_fans:
    a_t_fans = Fan.objects.filter(openid=s_openid)
    js_fan = WX_API.get_user_info(s_openid)
    if len(a_t_fans) == 0:
        mo_fan = Fan.convert_from_js(js_fan)
        mo_fan.save()
    else:
        mo_fan = a_t_fans[0]
    # user may modify nickname, so update this anyway
    mo_fan.nickname_b64 = base64.b64encode(js_fan['nickname'].encode('utf-8'))
    mo_fan.save()
    cnt += 1
    if 0 == cnt % 300:
        logging.debug('update %s wxfan' %(cnt))
    # get youzan user_id
    if mo_fan.yz_uid == 0:
        logging.debug('yz_uid is 0, so find it [%s]' %(mo_fan.yz_uid))
        dt_now = dt.datetime.now()
        d_api_param = {
            'app_id': '63ef9a4fc37047a97b',
            'timestamp': '%s' %(dt_now.strftime("%Y-%m-%d %H:%M:%S")),
            'v': '1.0',
# method param
            'method': 'kdt.users.weixin.follower.get',
            'weixin_openid': mo_fan.openid,
        }
        d_sort_param = sorted(d_api_param.iteritems())
        s_md5 = hashlib.md5(s_secret+''.join(['%s%s' %(v[0],v[1]) for v in d_sort_param])+s_secret).hexdigest()
        d_api_param['sign'] = s_md5
        s_url_param = '&'.join(['%s=%s' %(k, v) for k,v in d_api_param.iteritems()])
        s_url = 'http://open.koudaitong.com/api/entry?%s' %(urllib.urlencode(d_api_param))
        rq_ret = urllib2.urlopen(s_url)
        js_ret = json.loads(rq_ret.read())
        mo_fan.yz_uid = js_ret['response']['user']['user_id']
        mo_fan.save()

