#coding=utf-8
from django.db import models

# Create your models here.
# follow rfd doc

PRO_BJ = '北京'
Province_Choice = (
    (PRO_BJ, ''),
)

CTY_BEIJING = '北京市'
City_Choice = (
    (CTY_BEIJING, ''),
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
    (ARE_BJ_XICHENG,        ''),
    (ARE_BJ_TONGZHOU,       ''),
    (ARE_BJ_SHIJINGSHAN,    ''),
    (ARE_BJ_YANQING,        ''),
    (ARE_BJ_DONGCHENG,      ''),
    (ARE_BJ_FENGTAI,        ''),
    (ARE_BJ_FANGSHAN,       ''),
    (ARE_BJ_HAIDIAN,        ''),
    (ARE_BJ_CHAOYANG,       ''),
    (ARE_BJ_MIYUN,          ''),
    (ARE_BJ_PINGGU,         ''),
    (ARE_BJ_MENTOUGOU,      ''),
    (ARE_BJ_CHONGWEN,       ''),
    (ARE_BJ_DAXING,         ''),
    (ARE_BJ_CHANGPING,      ''),
    (ARE_BJ_HUAIROU,        ''),
    (ARE_BJ_SHUNYI,         ''),
    (ARE_BJ_XUANWU,         ''),
)

