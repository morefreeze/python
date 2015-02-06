#coding=utf-8
from django.db import models
from django.conf import settings
import logging
from jsonfield import JSONField
import hashlib
import uuid
import os
import datetime as dt

def get_cloth_filename(instance, filename):
    s_ext = os.path.splitext(filename)[1] # include dot, e.g.: ".png"
    if None == s_ext or '' == s_ext:
        s_ext = '.png'
    return os.path.join('clothes/', hashlib.md5(uuid.uuid4().__str__()).hexdigest())+s_ext

def get_avatar_filename(instance, filename):
    s_ext = os.path.splitext(filename)[1] # include dot, e.g.: ".png"
    if None == s_ext or '' == s_ext:
        s_ext = '.png'
    return os.path.join('avatar/', uuid.uuid4().__str__())+s_ext

def get_android_apk(instance, filename):
    s_ext = os.path.splitext(filename)[1] # include dot, e.g.: ".apk"
    if None == s_ext or '' == s_ext:
        s_ext = '.apk'
    return os.path.join('android/%s_%d' %(uuid.uuid4().__str__(), instance.ver_code))+s_ext

def get_android_latest_apk():
    s_ext = '.apk'
    return os.path.join(settings.MEDIA_ROOT, 'android/xilaile')+s_ext

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#Create your models here.
# score higher first
USER_LEVEL = [
    {'lower': 100000, 'name':u'铂金',},
    {'lower': 10000, 'name':u'黄金',},
    {'lower': 100, 'name':u'白银',},
    {'lower': 0, 'name':u'青铜',},
]
NO_LEVEL = u'暂无等级'

ONLINE_PAYMENT = ['alipay', 'wx', 'bfb', ]
# follow rfd doc

PRO_BJ = u'北京'
Province_Choice = (
    (PRO_BJ, PRO_BJ),
)

CTY_BEIJING = u'北京市'
City_Choice = (
    (CTY_BEIJING, CTY_BEIJING),
)

ARE_BJ_XICHENG = u'西城区'
ARE_BJ_TONGZHOU = u'通州区'
ARE_BJ_SHIJINGSHAN = u'石景山区'
ARE_BJ_YANQING = u'延庆县'
ARE_BJ_DONGCHENG = u'东城区'
ARE_BJ_FENGTAI = u'丰台区'
ARE_BJ_FANGSHAN = u'房山区'
ARE_BJ_HAIDIAN = u'海淀区'
ARE_BJ_CHAOYANG = u'朝阳区'
ARE_BJ_MIYUN = u'密云县'
ARE_BJ_PINGGU = u'平谷区'
ARE_BJ_MENTOUGOU = u'门头沟区'
ARE_BJ_CHONGWEN = u'崇文区'
ARE_BJ_DAXING = u'大兴区'
ARE_BJ_CHANGPING = u'昌平区'
ARE_BJ_HUAIROU = u'怀柔区'
ARE_BJ_SHUNYI = u'顺义区'
ARE_BJ_XUANWU = u'宣武区'
Area_Choice = (
    (ARE_BJ_XICHENG,        ARE_BJ_XICHENG),
    (ARE_BJ_TONGZHOU,       ARE_BJ_TONGZHOU),
    (ARE_BJ_SHIJINGSHAN,    ARE_BJ_SHIJINGSHAN),
    (ARE_BJ_YANQING,        ARE_BJ_YANQING),
    (ARE_BJ_DONGCHENG,      ARE_BJ_DONGCHENG),
    (ARE_BJ_FENGTAI,        ARE_BJ_FENGTAI),
    (ARE_BJ_FANGSHAN,       ARE_BJ_FANGSHAN),
    (ARE_BJ_HAIDIAN,        ARE_BJ_HAIDIAN),
    (ARE_BJ_CHAOYANG,       ARE_BJ_CHAOYANG),
    (ARE_BJ_MIYUN,          ARE_BJ_MIYUN),
    (ARE_BJ_PINGGU,         ARE_BJ_PINGGU),
    (ARE_BJ_MENTOUGOU,      ARE_BJ_MENTOUGOU),
    (ARE_BJ_CHONGWEN,       ARE_BJ_CHONGWEN),
    (ARE_BJ_DAXING,         ARE_BJ_DAXING),
    (ARE_BJ_CHANGPING,      ARE_BJ_CHANGPING),
    (ARE_BJ_HUAIROU,        ARE_BJ_HUAIROU),
    (ARE_BJ_SHUNYI,         ARE_BJ_SHUNYI),
    (ARE_BJ_XUANWU,         ARE_BJ_XUANWU),
)

