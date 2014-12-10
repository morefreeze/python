#coding=utf-8
from django.db import models
from django.conf import settings
from jsonfield import JSONField
import hashlib
import uuid
import os

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

#Create your models here.
# score higher first
USER_LEVEL = [
    {'lower': 100000, 'name':'铂金',},
    {'lower': 10000, 'name':'黄金',},
    {'lower': 100, 'name':'白银',},
    {'lower': 0, 'name':'青铜',},
]
NO_LEVEL = '暂无等级'
# follow rfd doc

PRO_BJ = '北京'
Province_Choice = (
    (PRO_BJ, PRO_BJ),
)

CTY_BEIJING = '北京市'
City_Choice = (
    (CTY_BEIJING, CTY_BEIJING),
)

ARE_BJ_XICHENG = '西城区'
ARE_BJ_TONGZHOU = '通州区'
ARE_BJ_SHIJINGSHAN = '石景山区'
ARE_BJ_YANQING = '延庆县'
ARE_BJ_DONGCHENG = '东城区'
ARE_BJ_FENGTAI = '丰台区'
ARE_BJ_FANGSHAN = '房山区'
ARE_BJ_HAIDIAN = '海淀区'
ARE_BJ_CHAOYANG = '朝阳区'
ARE_BJ_MIYUN = '密云县'
ARE_BJ_PINGGU = '平谷区'
ARE_BJ_MENTOUGOU = '门头沟区'
ARE_BJ_CHONGWEN = '崇文区'
ARE_BJ_DAXING = '大兴区'
ARE_BJ_CHANGPING = '昌平区'
ARE_BJ_HUAIROU = '怀柔区'
ARE_BJ_SHUNYI = '顺义区'
ARE_BJ_XUANWU = '宣武区'
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

