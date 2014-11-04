# coding=utf-8
from django.db import models
from jsonfield import JSONField
from WCUser.models import User, Shop
from WCLogistics.models import RFD, Address
from WCCloth.models import Cloth
import json

# Create your models here.
class Bill(models.Model):
    bid = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    get_time_0 = models.DateTimeField()
    get_time_1 = models.DateTimeField()
    return_time_0 = models.DateTimeField()
    return_time_1 = models.DateTimeField()
    own = models.ForeignKey(User) # own_id in db
    lg = models.ForeignKey(RFD,null=True) # lg_id in db
    adr = models.ForeignKey(Address) # adr_id in db
    shop = models.ForeignKey(Shop,null=True)
    status = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    total = models.FloatField(default=0.0)
    clothes = JSONField(default=[])
    ext = JSONField(default={})

    def __unicode__(self):
        return self.bid

# update total field
    def calc_total(self):
        f_total = 0.0
        try:
            js_cloth = self.clothes
            for it_cloth in js_cloth:
                try:
                    i_cid = it_cloth.get('cid')
                    i_num = it_cloth.get('number')
                    mo_cloth = Cloth.objects.get(cid=i_cid)
                    f_price = mo_cloth.price
                except (AttributeError, Cloth.DoesNotExist) as e:
                    self.ext['error'] = "%s%s(it_cloth:%s);" \
                        %(self.ext.get('error', ''), e.__str__(), it_cloth.__str__())
                    continue
                if i_num * f_price <= 0:
                    self.ext['error'] = "%s%s(it_cloth:%s);" \
                        %(self.ext.get('error', ''), 'num*price<0', it_cloth.__str__())
                else:
                    f_total += i_num * f_price
        except (ValueError) as e:
            self.ext['error'] = "%s%s(it_cloth:%s);" \
                %(self.ext.get('error', ''), e.__str__(), it_cloth.__str__())
            f_total = 0.0
        self.total = f_total
        return f_total

    @classmethod
    def get_bill(cls, own_id, bid):
        try:
            mo_bill = cls.objects.get(own_id=own_id, bid=bid)
        except (cls.DoesNotExist) as e:
            return None
        return mo_bill

    @classmethod
    def get_bills(cls, own_id, pn=1, deleted=0, rn=10):
        l_bill = cls.objects.filter(own_id=own_id)[(pn-1)*rn:pn*rn]
        return l_bill

class Coupon(models.Model):
    coid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    expire_time = models.DateTimeField()
# exp threshold user's exp must greater than this
    exp_thd = models.IntegerField(default=0)
# cloth threshold this can be first category, bill must contain at least one
# cloth which cid equal cid_thd
    cid_thd = models.ForeignKey(Cloth, blank=True, null=True)
# price threshold total price greater than this
    price_thd = models.FloatField(default=0)
# percent discount [0,100] like 10% off
    percent_dst = models.IntegerField(default=0)
# price discount minus price directly
    price_dst = models.FloatField(default=0)

    def __unicode__(self):
        return self.name
