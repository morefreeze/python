# coding=utf-8
from WCLib.models import *
from WCLib.views import *
from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from WCUser.models import User, Shop
from WCLogistics.models import RFD, Address
from WCCloth.models import Cloth
from WCCloth.serializers import ClothSerializer
import json

# Create your models here.
class Mass_Clothes(models.Model):
    class Meta:
        abstract = True

    clothes = JSONField(default=[])
    ext = JSONField(default={})
    def add_error(self, s_errmsg):
        if None == self.ext:
            self.ext = {}
        if None == self.ext.get('error'):
            self.ext['error'] = []
        self.ext['error'].append(s_errmsg)

    def clear_error(self):
        if None == self.ext:
            self.ext = {}
        self.ext['error'] = []

    # format_cloth DOES NOT save
    # but modify clothes value
    def format_cloth(self, s_cloth=None):
        if None == self.ext:
            self.ext = {}
        try:
            if None != s_cloth and '' != s_cloth:
                a_clothes = json.loads(s_cloth)
            else:
                a_clothes = self.clothes
            a_new_clothes = []
            for it_cloth in a_clothes:
                if 'cid' not in it_cloth:
                    raise ValueError('cid not in cloth')
                if 'number' not in it_cloth:
                    raise ValueError('number not in cloth')
                mo_cloth = Cloth.objects.get(cid=it_cloth['cid'])
                if not mo_cloth.is_leaf:
                    raise Cloth.DoesNotExist('cloth[%d] is not leaf %d' % mo_cloth.cid)
                js_cloth = {}
                se_cloth = ClothSerializer(mo_cloth)
                js_cloth['cid'] = se_cloth.data['cid']
                js_cloth['number'] = it_cloth['number']
                js_cloth['name'] = se_cloth.data['name']
                js_cloth['price'] = se_cloth.data['price']
                js_cloth['image'] = se_cloth.data['image']
                a_new_clothes.append(js_cloth)
            self.clothes = a_new_clothes
        except (ValueError,Cloth.DoesNotExist) as e:
            self.add_error(e.__str__())
            return []
        self.ext['format_cloth'] = True
        return self.clothes

"""
# JSONField has bug, if parent has JSONField will be escaped after update
# so decode it expect insert
    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                self.clothes = json.loads(self.clothes)
            except Exception as e:
                self.clothes = self.clothes
            try:
                self.ext = json.loads(self.ext)
            except Exception as e:
                self.ext = self.ext
        else:
            self.clothes = self.clothes
            self.ext = self.ext

# don't write self.__class__ in abstract, it will be derive class
        super(Mass_Clothes, self).save(*args, **kwargs)
        """

SCORE_RMB_RATE = 0.01
class Bill(Mass_Clothes):
    READY = 0
    CONFIRMING = 10
    WAITTING_GET = 20
    GETTING = 25
    WASHING = 30
    RETURNNING = 40
    NEED_FEEDBACK = 50
    DONE = 60
    USER_CANCEL = -10
    ERROR = -20

    LOWEST_SHIPPING_FEE = 49.0
    SHIPPING_FEE = 10.0

    bid = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    get_time_0 = models.DateTimeField()
    get_time_1 = models.DateTimeField()
    return_time_0 = models.DateTimeField()
    return_time_1 = models.DateTimeField()
    own = models.ForeignKey(User) # own_id in db
    lg = models.OneToOneField(RFD,null=True, related_name='bill_of') # lg_id in db
    province = models.CharField(max_length=15,default='',choices=Province_Choice)
    city = models.CharField(max_length=63,default='',choices=City_Choice)
    area = models.CharField(max_length=15,default='',choices=Area_Choice)
    address = models.CharField(max_length=511, default='')
    phone = models.CharField(max_length=12,default='')
    real_name = models.CharField(max_length=255,default='')
    shop = models.ForeignKey(Shop,null=True)
    status = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    total = models.FloatField(default=0.0)
    paid = models.FloatField(default=0.0)
    comment = models.CharField(max_length=1023, default='', blank=True)

    def __unicode__(self):
        return "%d" %(self.bid)

    def get_full_address(self):
        if 0 == len(self.province + self.city + self.area):
            s_separator = ''
        else:
            s_separator = ' '
        return self.province + self.city + self.area + s_separator + self.address

# update total field
    def calc_total(self):
        f_total = 0.0
        if None == self.ext:
            self.ext = {}
        if not self.ext.get('format_cloth'):
            self.clothes = self.format_cloth()
        js_cloth = self.clothes
        while True:
            if 0 == len(js_cloth):
                self.add_error('clothes is empty')
                break
            for it_cloth in js_cloth:
                try:
                    i_cid = it_cloth.get('cid')
                    i_num = it_cloth.get('number')
                    mo_cloth = Cloth.objects.get(cid=i_cid,is_leaf=True)
                    f_price = mo_cloth.price
                except (AttributeError, Cloth.DoesNotExist) as e:
                    self.add_error("%s(it_cloth:%s,maybe category)" \
                        %(e.__str__(), it_cloth.__str__()))
                    continue
                if i_num * f_price < 0:
                    self.add_error("%s(it_cloth:%s)" \
                        %('num*price<0', it_cloth.__str__()))
                else:
                    f_total += i_num * f_price
            if self.score >= 0:
                if f_total - self.score * SCORE_RMB_RATE < 0:
                    self.add_error('score exceed total price')
                else:
                    f_total -= self.score * SCORE_RMB_RATE
# coupon calc
            i_mcid = self.ext.get('use_coupon') or 0
            if i_mcid > 0:
                try:
                    mo_mycoupon = MyCoupon.objects.get(mcid=i_mcid)
                    mo_cloth_thd = mo_mycoupon.cid_thd
# all bill clothes is belong cid_thd
                    if None != mo_cloth_thd:
                        for it_cloth in js_cloth:
                            if not Cloth.is_ancestor(mo_cloth_thd.cid, it_cloth['cid']):
                                raise ValueError("cid[%d] is not belong %s" %(it_cloth['cid'], mo_cloth_thd))
                    if f_total < mo_mycoupon.price_thd:
                        raise ValueError("total is not enough")
                    if mo_mycoupon.percent_dst > 0:
                        f_total *= mo_mycoupon.percent_dst * 0.01
                    f_total -= mo_mycoupon.price_dst
                except (ValueError, MyCoupon.DoesNotExist) as e:
                    self.add_error(e.__str__())
                    del self.ext['use_coupon']
# coupon calc end
# shipping fee
            if f_total < self.LOWEST_SHIPPING_FEE:
                f_total += SHIPPING_FEE
                self.ext['shipping_fee'] = True
            else:
                self.ext['shipping_fee'] = False
# shipping fee end
            break # while True
        self.total = f_total
        self.ext['calc_total'] = True
        return f_total

    def is_inquiry(self):
        js_cloth = self.clothes
        if self.comment != '':
            self.ext['inquiry'] = True
            return True
        for it_cloth in js_cloth:
            try:
                i_cid = it_cloth.get('cid')
                mo_cloth = Cloth.objects.get(cid=i_cid,is_leaf=True)
                if 'inquiry' in mo_cloth.ext and mo_cloth.ext['inquiry']:
                    self.ext['inquiry'] = True
                    return True
            except (AttributeError, Cloth.DoesNotExist) as e:
                self.ext['error'] = "%s%s(it_cloth:%s,maybe category);" \
                    %(self.ext.get('error', ''), e.__str__(), it_cloth.__str__())
                continue
        return False

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
# cloth which cid equal cid_thd, null represent all clothes
    cid_thd = models.ForeignKey(Cloth, blank=True, null=True)
# price threshold total price greater than this
    price_thd = models.FloatField(default=0)
# percent discount [0,100] like 10% off, percent discount will be calc before price
    percent_dst = models.IntegerField(default=0)
# price discount minus price directly
    price_dst = models.FloatField(default=0)
# max use limit each user, 0 for no limit
    max_limit = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

class MyCoupon(models.Model):
    CAN_USE = 1
    NOUSED = 2
    USED_OR_EXPIRE = 3
    ALL = 9

    mcid = models.AutoField(primary_key=True)
    own = models.ForeignKey('WCUser.User', db_index=True)
    used = models.BooleanField(default=False)
    start_time = models.DateTimeField(default=dt.datetime(2000,1,1))
    expire_time = models.DateTimeField(default=dt.datetime(2000,1,1))
    cid_thd = models.ForeignKey(Cloth, blank=True, null=True)
    price_thd = models.FloatField(default=0)
    percent_dst = models.IntegerField(default=0)
    price_dst = models.FloatField(default=0)
    ext = JSONField(default={})

    def __unicode__(self):
        if None == self.cid_thd:
            return "%s([%.0f,%s] -%.0f -%d%%)" %(self.own.name, self.price_thd, \
                        'ALL', self.price_dst, self.percent_dst)

        return "%s([%.0f,%s] -%.0f -%d%%)" % (self.own.name, self.price_thd, \
                        self.cid_thd.name, self.price_dst, self.percent_dst)

    @classmethod
    def query_mycoupons(cls, mo_user, i_type):
        if None == mo_user:
            return None
        dt_now = dt.datetime.now()
        if MyCoupon.CAN_USE == i_type:
            a_mycoupons = MyCoupon.objects.filter(own=mo_user, used=False, \
                            start_time__lte = dt_now, expire_time__gt = dt_now)
        elif MyCoupon.NOUSED == i_type:
            a_mycoupons = MyCoupon.objects.filter(own=mo_user, used=False, \
                            start_time__gte = dt_now, expire_time__gt = dt_now)
        elif MyCoupon.USED_OR_EXPIRE == i_type:
            a_mycoupons = MyCoupon.objects.filter(Q(own=mo_user) & (Q(used=True) \
                            | Q(expire_time__lte = dt_now)))
        elif MyCoupon.ALL == i_type:
            a_mycoupons = MyCoupon.objects.filter(own=mo_user)
        else:
            return None
        a_mycoupons = a_mycoupons.order_by('used', 'start_time', 'expire_time', 'mcid')
        return a_mycoupons

# return False or bill.total
    def is_vali(self, mo_bill):
        if None == mo_bill:
            return False
        if mo_bill.own != self.own:
            return False
        if self.used:
            return False
        dt_now = dt.datetime.now()
        if dt_now < self.start_time or dt_now >= self.expire_time:
            return False
# fake bill just validate coupon
        t_bill = Bill(clothes=mo_bill.clothes)
        t_bill.ext['use_coupon'] = self.mcid
        t_bill.calc_total()
        if None != t_bill.ext.get('error') or None == t_bill.ext.get('use_coupon'):
            print t_bill.ext
            return False
        return t_bill.total

class Feedback(models.Model):
    fid = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField(default=5)
    content = models.CharField(max_length=1023)

class Cart(Mass_Clothes):
    caid = models.AutoField(primary_key=True)
    own = models.ForeignKey(User, unique=True)
    update_time = models.DateTimeField(auto_now=True)

    @classmethod
# return caid
    def remove_bill_clothes(cls, own, mo_bill):
        try:
            mo_cart = cls.objects.get(own=own)
        except (cls.DoesNotExist):
            return -1
        d_del_cloth = {}
        for it_cloth in mo_bill.clothes:
            if 'cid' in it_cloth:
                d_del_cloth[ it_cloth['cid'] ] = 1
        mo_cart.ext = d_del_cloth
        a_new_clothes = []
        mo_cart.ext['e'] = []
        for it_cloth in mo_cart.clothes:
            mo_cart.ext['e'].append(it_cloth)
            if 'cid' in it_cloth and it_cloth['cid'] not in d_del_cloth:
                a_new_clothes.append(it_cloth)
        mo_cart.clothes = a_new_clothes
        mo_cart.save()
        return mo_cart.caid

