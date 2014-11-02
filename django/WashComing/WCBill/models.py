# coding=utf-8
from django.db import models
from jsonfield import JSONField
from WCUser.models import User, Shop
from WCLogistics.models import RFD, Address
from WCCloth.models import Cloth

# Create your models here.
class Bill(models.Model):
    bid = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    get_time = models.DateTimeField()
    return_time = models.DateTimeField()
    own = models.ForeignKey(User) # own_id in db
    lg = models.ForeignKey(RFD,null=True) # lg_id in db
    adr = models.ForeignKey(Address) # adr_id in db
    shop = models.ForeignKey(Shop,null=True)
    status = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    clothes = JSONField(default=None)
    ext = JSONField(default=None)

    def __unicode__(self):
        return self.bid

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
