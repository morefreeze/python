# coding=utf-8
import base
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from WCBill.models import *
from WCUser.models import *
mo_user = User.objects.get(pk=188) #it is lcx account
a_c = Coupon.objects.filter(name='xxxxxxxx')
for it_coupon in a_c:
    it_coupon.add_user(mo_user)
