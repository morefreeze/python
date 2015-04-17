# coding=utf-8
from WCLib.models import *
from WCLib.views import *
from django.db import models
import json
import ConfigParser
import datetime as dt

# Create your models here.
import urllib, urllib2

# keep last MAX_KEEP access token(in fact only last two are valid)
class Access_Token(models.Model):
    at_id = models.AutoField(primary_key=True)
    access_token = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    expire_time = models.DateTimeField()

    _access_token = None
    _expire_time = None
    MAX_KEEP = 10
# in parent directory
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    config = ConfigParser.ConfigParser()

    def __unicode__(self):
        return '%s [%s] [%s]' %(self.at_id, self.access_token, self.expire_time)

    @classmethod
    def get_access_token(cls):
        dt_now = dt.datetime.now()
        if None != cls._expire_time and None != cls._access_token and cls._expire_time > dt_now:
            return cls._access_token
# need get from db
        a_at = cls.objects.filter(expire_time__gt=dt_now).order_by('-at_id')
        if len(a_at) > 0:
            cls._access_token = a_at[0].access_token
            cls._expire_time = a_at[0].expire_time
            return cls._access_token
# need get a new access token
        with open(os.path.join(cls.conf_dir, 'weixin.conf'), 'r') as wxconf:
            cls.config.readfp(wxconf)
            s_appid = cls.config.get('common', 'appid')
            s_secret = cls.config.get('common', 'secret')
            s_get_token_url = cls.config.get('basic', 'get_token_url')
        d_get = {
            'grant_type':   'client_credential',
            'appid':        s_appid,
            'secret':       s_secret,
        }
        s_get = urllib.urlencode(d_get)
        s_url = s_get_token_url + '?' + s_get
        req = urllib2.Request(s_url)
        response = urllib2.urlopen(req)
        page = response.read()
        js_req = json.loads(page)
        if 'access_token' in js_req:
            cls._access_token = js_req['access_token']
            cls._expire_time = dt_now + dt.timedelta(seconds=int(js_req['expires_in']))
            cls.objects.create(access_token=cls._access_token, expire_time=cls._expire_time)
# keep MAX_KEEP access token, remove other
            a_keep_at = cls.objects.all().order_by('-at_id')[:cls.MAX_KEEP]
            i_keep_len = len(a_keep_at)
            if i_keep_len > 0:
                cls.objects.filter(at_id__lt=a_keep_at[i_keep_len-1].at_id).delete()
            return cls._access_token
        return ''

class WX_API:
# in parent directory
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    config = ConfigParser.ConfigParser()

    @classmethod
# limit=None for all users
# wx return {'total':1421, 'count':1421, data:{'openid':['oP1a0txxxxxx', ...]}, 'next_openid':'oP1a0tyyyyyy'}
    def get_users(cls, limit=None):
        with open(os.path.join(cls.conf_dir, 'weixin.conf'), 'r') as wxconf:
            cls.config.readfp(wxconf)
            s_get_users_url = cls.config.get('user', 'get_users_url')
        js_req = cls.do_send_api(s_get_users_url)
        if 'errcode' in js_req and js_req['errcode']:
            logging.error(js_req)
            return []
        a_ret = []
        if None == limit:
            limit = js_req['total']
        while limit > len(a_ret):
            i_need_len = limit - len(a_ret)
            a_ret += js_req['data']['openid'][:i_need_len]
            if js_req['total'] == js_req['total'] or 0 == js_req['count']:
                break
            js_req = cls.do_send_api(s_get_users_url, {'next_openid': js_req['next_openid']})
        return a_ret

    @classmethod
    def get_user_info(cls, openid):
        with open(os.path.join(cls.conf_dir, 'weixin.conf'), 'r') as wxconf:
            cls.config.readfp(wxconf)
            s_get_user_info_url = cls.config.get('user', 'get_user_info_url')
        js_req = cls.do_send_api(s_get_user_info_url, {'openid': openid})
        if 'errcode' in js_req and js_req['errcode']:
            logging.error(js_req)
            return {}
        return js_req

    @classmethod
    def send_kf_msg(cls, openid, msg, kf_name=None):
        with open(os.path.join(cls.conf_dir, 'weixin.conf'), 'r') as wxconf:
            cls.config.readfp(wxconf)
            s_custom_send_url = cls.config.get('msg', 'custom_send_url')
        d_body = {
            "touser": openid,
            "msgtype": "text",
            "text": {
                "content": msg
            },
        }
        if None != kf_name:
            d_body['customservice'] = {}
            d_body['customservice']['kf_account'] = kf_name
        s_body = json.dumps(d_body, ensure_ascii=True)
        js_req = cls.do_send_api(s_custom_send_url, None, s_body)
        if 'errcode' in js_req and js_req['errcode']:
            logging.error(js_req)
            return {}
        return js_req

    @classmethod
    # param={'param1': {'value':'xxx', 'color':'#123456'}, ...}
    def send_template_msg(cls, openid, template_id, param, topcolor='#000000'):
        with open(os.path.join(cls.conf_dir, 'weixin.conf'), 'r') as wxconf:
            cls.config.readfp(wxconf)
            s_template_send_url = cls.config.get('msg', 'template_send_url')
        d_body = {
            "touser": openid,
            "template_id": template_id,
            "url":"http://weixin.qq.com/download",
            "topcolor":topcolor,
            "data": param,
        }
        s_body = json.dumps(d_body, ensure_ascii=True)
        js_req = cls.do_send_api(s_template_send_url, None, s_body)
        if 'errcode' in js_req and js_req['errcode']:
            logging.error(js_req)
            return {}
        return js_req

    @classmethod
    def do_send_api(cls, url, d_get=None, body=None):
        s_access_token = Access_Token.get_access_token()
        header = {'Content-Type': 'application/json'}
        if None == d_get:
            d_get = {}
        d_get['access_token'] = s_access_token
        s_get = urllib.urlencode(d_get)
        s_url = url + '?' + s_get
        req = urllib2.Request(s_url, body, header)
        response = urllib2.urlopen(req)
        page = response.read()
# damn character
        import re
        page = re.sub(ur'[\x0f\x0e\x0d\x0c\x0b\x0a]', '', page)
        js_ret = json.loads(page)
        return js_ret

class Fan(models.Model):
    openid = models.CharField(primary_key=True, max_length=63)
# be careful, youzan will trim nickname space, so you'd better use %name%
    nickname = models.CharField(db_index=True, max_length=255)
    nickname_b64 = models.CharField(default='', max_length=1023)
    yz_uid = models.IntegerField(default=0)
    subscribe = models.BooleanField(default=True)
    subscribe_time = models.IntegerField()
    sex = models.IntegerField()
    country = models.CharField(max_length=31)
    province = models.CharField(max_length=31)
    city = models.CharField(max_length=31)
    headimgurl = models.CharField(max_length=255)
    remark = models.CharField(max_length=255)

    @classmethod
    def convert_int_hex(cls, x):
        s = '0123456789ABCDEF'
        pow = 16
        s_ret = ''
        while x > 0:
            s_ret = s[x % 16] + s_ret
            x /= pow
        return s_ret

    @classmethod
# convert from get_user_info json
    def convert_from_js(cls, js_info):
        import re
        mo_ret = cls()
        mo_ret.openid = js_info.get('openid')
        s_patt = ur'[^\u4e00-\u9fa5\u0000-\u007f]'
        mo_ret.nickname = js_info.get('nickname')
        while True:
            re_out = re.search(s_patt, mo_ret.nickname)
            if None == re_out:
                break
            mo_ret.nickname = re.sub(s_patt, '[0X'+cls.convert_int_hex(ord(re_out.group(0)))+']', mo_ret.nickname, 1)
        mo_ret.subscribe = js_info.get('subscribe')
        mo_ret.subscribe_time = js_info.get('subscribe_time')
        mo_ret.sex = js_info.get('sex')
        mo_ret.country = js_info.get('country')
        mo_ret.province = js_info.get('province')
        mo_ret.city = js_info.get('city')
        mo_ret.headimgurl = js_info.get('headimgurl')
        mo_ret.remark = js_info.get('remark')
        return mo_ret

class YZ_API(AbstractConf):
    conf_name = 'youzan.conf'

    @classmethod
    def do_send_api(cls, s_method, d_param=None):
        dt_now = dt.datetime.now()
        a_conf_pair = [
            {'section': 'common',
             'name':    'url',
            },
            {'section': 'common',
             'name':    'app_id',
            },
            {'section': 'common',
             'name':    'secret',
            },
        ]
        [s_url, s_app_id, s_secret] = cls.read_conf(a_conf_pair)
        d_api_param = {
            'app_id': s_app_id,
            'method': s_method,
            'timestamp': '%s' %(dt_now.strftime("%Y-%m-%d %H:%M:%S")),
            'v': '1.0',
        }
        if None != d_param:
            d_api_param.update(d_param)
        d_sort_param = sorted(d_api_param.iteritems())
        s_md5 = hashlib.md5(s_secret+''.join(['%s%s' %(v[0],v[1]) for v in d_sort_param])+s_secret).hexdigest()
        d_api_param['sign'] = s_md5
        s_url_param = urllib.urlencode(d_api_param)
        s_url = '%s?%s' %(s_url, s_url_param)
        rq_ret = urllib2.urlopen(s_url)
        js_ret = json.loads(rq_ret.read())
        if 'error_response' in js_ret or 'response' not in js_ret:
            logging.error(js_ret)
            return {}
        return js_ret['response']

    @classmethod
    def get_sold_list(cls, fields=None, status=None, start_update=None, end_update=None, limit=None):
        page_no = 1
        i_total = 0
        a_ret = []
        while True:
            d_param = {
                'fields': fields,
                'status': status,
                'start_update': start_update,
                'end_update': end_update,
                'page_no': page_no,
                'page_size': 50,
            }
            js_ret = cls.do_send_api('kdt.trades.sold.get', d_param)
            if 'trades' not in js_ret:
                break
            i_len = len(js_ret['trades'])
            if 0 == i_len:
                break
            i_total += i_len
            if limit != None and i_total >= limit:
                a_ret += js_ret['trades'][:limit-len(a_ret)]
            else:
                a_ret += js_ret['trades']
            if 'total_results' not in js_ret or int(js_ret['total_results']) <= i_total:
                break
        return a_ret

    @classmethod
# b_no_exp==1 then no need express
# exp_name will get 'exp_xxx' in conf code
# outer_tid outside bill id
# out_sid express bill id
# return is success or not
    def confirm_send(cls, tid, b_no_exp, exp_name='', outer_tid=None, out_sid=None):
        if b_no_exp:
            d_param = {
                'tid': tid,
                'is_no_express': b_no_exp,
            }
        else:
            a_out = cls.read_conf([{'section': 'logistics', 'name': 'exp_%s' %(exp_name)}])
            if 0 == len(a_out):
                logging.error('%s is not valid express name' %(exp_name))
                return False
            out_stype = int(a_out[0])
            d_param = {
                'tid': tid,
                'is_no_express': b_no_exp,
                'outer_tid': outer_tid,
                'out_stype': out_stype,
                'out_sid': out_sid,
            }
        js_ret = cls.do_send_api('kdt.logistics.online.confirm', d_param)
        if 'shipping' in js_ret and 'is_success' in js_ret['shipping']:
            return js_ret['shipping']['is_success']
        return False

