# coding=utf-8
from WCLib.models import *
from WCLib.views import *
from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from WCUser.models import User, Shop
from WCLogistics.models import RFD, Address, OrderQueue
from WCCloth.models import Cloth
from WCCloth.serializers import ClothSerializer
import ConfigParser
import json
import pingpp

# Create your models here.
class Mass_Clothes(models.Model):
    class Meta:
        abstract = True

    clothes = JSONField(default=[], verbose_name=u'衣物')
    ext = JSONField(default={}, verbose_name=u'扩展字段')
    def add_error(self, s_errmsg):
        if None == self.ext:
            self.ext = {}
        if None == self.ext.get('error'):
            self.ext['error'] = []
        self.ext['error'].append(s_errmsg)

    def clear_ext(self):
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
                js_cloth['number'] = int(it_cloth['number'])
                js_cloth['price'] = float(se_cloth.data['price'])
                mo_fa_cloth = mo_cloth.fa_cid
                if None == mo_fa_cloth or None == mo_fa_cloth.fa_cid:
# second category
                    js_cloth['image'] = se_cloth.data['image']
                    js_cloth['name'] = se_cloth.data['name']
                else:
# third category
                    se_fa_cloth = ClothSerializer(mo_fa_cloth)
                    js_cloth['image'] = se_fa_cloth.data['image']
                    js_cloth['name'] = "%s(%s)" \
                            %(se_fa_cloth.data['name'], se_cloth.data['name'])
                a_new_clothes.append(js_cloth)
            self.clothes = a_new_clothes
        except (ValueError,Cloth.DoesNotExist) as e:
            self.add_error(e.__str__())
            return []
        self.ext['format_cloth'] = True
        return self.clothes

SCORE_RMB_RATE = 0.01
class Bill(Mass_Clothes):
    READY = 0
    NOT_PAID = 5
    CONFIRMING = 10
    WAITTING_GET = 20
    GETTING = 25
    WASHING = 30
    RETURNNING = 40
    NEED_FEEDBACK = 50
    DONE = 60
    USER_CANCEL = -10
    ADMIN_CANCEL = -15
    ERROR = -20
    StatusChoices = (
        (READY,         u'准备'),
        (NOT_PAID,      u'未支付'),
        (CONFIRMING,    u'订单确认中'),
        (WAITTING_GET,  u'物流确认中'),
        (GETTING,       u'取衣中'),
        (WASHING,       u'洗衣中'),
        (RETURNNING,    u'送衣中'),
        (NEED_FEEDBACK, u'待评价'),
        (DONE,          u'订单完成'),
        (USER_CANCEL,   u'用户取消'),
        (ADMIN_CANCEL,  u'管理员取消'),
        (ERROR,         u'发生错误'),
    )

    LOWEST_SHIPPING_FEE = 39.0
    SHIPPING_FEE = 10.0

    bid = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    get_time_0 = models.DateTimeField(verbose_name=u'取衣开始时间')
    get_time_1 = models.DateTimeField(verbose_name=u'取衣结束时间')
    return_time_0 = models.DateTimeField(verbose_name=u'送衣开始时间')
    return_time_1 = models.DateTimeField(verbose_name=u'送衣结束时间')
    own = models.ForeignKey(User,verbose_name=u'下单用户') # own_id in db
    lg = models.OneToOneField(RFD,blank=True,null=True, related_name='bill_of', verbose_name=u'物流') # lg_id in db
    province = models.CharField(max_length=15,default='',choices=Province_Choice, verbose_name=u'省')
    city = models.CharField(max_length=63,default='',choices=City_Choice, verbose_name=u'市')
    area = models.CharField(max_length=15,default='',choices=Area_Choice, verbose_name=u'区')
    address = models.CharField(max_length=511, default='', verbose_name=u'地址')
    phone = models.CharField(max_length=12,default='', verbose_name=u'手机')
    real_name = models.CharField(max_length=255,default='', verbose_name=u'姓名')
    shop = models.ForeignKey(Shop,blank=True,null=True, verbose_name=u'店铺')
    status = models.IntegerField(default=READY,choices=StatusChoices, verbose_name=u'订单状态')
    deleted = models.BooleanField(default=False, verbose_name=u'删除标志')
    score = models.PositiveIntegerField(default=0, verbose_name=u'使用积分')
    total = models.FloatField(default=0.0, verbose_name=u'总价')
    paid = models.FloatField(default=0.0, verbose_name=u'已付款')
    comment = models.CharField(max_length=1023, default='', blank=True, verbose_name=u'留言')
    admin_comment = models.CharField(max_length=1023, default='', blank=True, verbose_name=u'管理员留言')
    shop_comment = models.CharField(max_length=1023, default='', blank=True, verbose_name=u'店铺留言')

    @classmethod
    def get_status(cls, i_status):
        map = dict(cls.StatusChoices)
        if i_status in map:
            return map[i_status]
        return u'未知'

    def __unicode__(self):
        s_ret = ''
        s_ret += u"%d " %(self.bid)
        if self.paid > 0:
            s_ret += u"￥%.2f(已支付%.2f) " %(self.total, self.paid)
        elif self.ext and self.ext.get('payment') in ONLINE_PAYMENT:
            s_ret += u"￥%.2f(未支付) " %(self.total)
        else:
            s_ret += u"￥%.2f(现金) " %(self.total)

        s_ret += u"[%s] [%s~%s] [%s] [%s %s] [%s] 留言[%s] 管理员[%s] 店铺[%s])" %(Bill.get_status(self.status), self.get_time_0.strftime('%m-%d %H'), self.return_time_0.strftime('%m-%d %H'), self.real_name, \
                self.area, self.address, self.phone, self.comment, self.admin_comment, self.shop_comment)
        return s_ret

    def change_status(self, i_status):
        if i_status < Bill.READY or (i_status >= Bill.READY and self.status < i_status):
            self.status = i_status
            self.add_time(i_status)

# add until current(<=status) status timestamp to log
    def add_time(self, pi_status):
        if None == self.ext:
            self.ext = {}
        if 'lg_time' not in self.ext:
            self.ext['lg_time'] = {}
        pi_status = int(pi_status or 0)
        if pi_status < Bill.ERROR or pi_status > Bill.DONE:
            pi_status = Bill.ERROR
        for i_status, s_ch in self.StatusChoices:
            if i_status < 0:
                continue
            if pi_status < i_status:
                continue
# in sql it save as string instead of int
# current status must update
            if str(i_status) not in self.ext['lg_time'] or i_status == pi_status:
                self.ext['lg_time'][str(i_status)] = dt.datetime.now()

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
                    i_cid = it_cloth['cid']
                    i_num = int(it_cloth['number'])
                    f_price = float(it_cloth['price'])
                except (AttributeError, Cloth.DoesNotExist) as e:
                    self.add_error("%s(it_cloth:%s,maybe category)" \
                        %(e.__str__(), it_cloth.__str__()))
                    continue
                if i_num * f_price < 0:
                    self.add_error("%s(it_cloth:%s)" \
                        %('num*price<0', it_cloth.__str__()))
                else:
                    f_total += i_num * f_price
            self.ext['old_total'] = f_total
# shipping fee
            if f_total < self.LOWEST_SHIPPING_FEE:
                f_total += Bill.SHIPPING_FEE
                self.ext['shipping_fee'] = Bill.SHIPPING_FEE
            else:
                self.ext['shipping_fee'] = 0.0
# shipping fee end
# coupon calc
            i_mcid = self.ext.get('use_coupon') or 0
            if i_mcid > 0:
# use for calc mycoupon
                f_cid_total = 0.0
                try:
                    mo_mycoupon = MyCoupon.objects.get(mcid=i_mcid, used=False)
                    mo_cloth_thd = mo_mycoupon.cid_thd
# all bill clothes is belong cid_thd
                    if None != mo_cloth_thd:
                        for it_cloth in js_cloth:
                            i_cid = it_cloth['cid']
                            i_num = it_cloth['number']
                            f_price = it_cloth['price']
                            if Cloth.is_ancestor(mo_cloth_thd.cid, i_cid):
                                f_cid_total += max(0, i_num*f_price)
                    else:
# all category, so all clothes will apply discount
                        f_cid_total += f_total

                    logging.debug("f_cid[%.2f] price_thd[%.2f]" %(f_cid_total, mo_mycoupon.price_thd))
                    f_old_cid_total = f_cid_total
                    if f_cid_total < mo_mycoupon.price_thd:
                        raise ValueError("cid total is not enough")
                    if mo_mycoupon.percent_dst > 0:
                        f_cid_total *= (100-mo_mycoupon.percent_dst) * 0.01
                        self.ext['percent_dst'] = f_old_cid_total - f_cid_total
                    f_cid_total -= mo_mycoupon.price_dst
                    self.ext['price_dst'] = mo_mycoupon.price_dst
                    f_total -= f_old_cid_total - f_cid_total
                except (ValueError, MyCoupon.DoesNotExist) as e:
                    self.add_error(e.__str__())
                    del self.ext['use_coupon']
# coupon calc end

# score calc
            if self.score >= 0:
                if f_total - self.score * SCORE_RMB_RATE < 0:
                    self.add_error('score exceed total price')
                else:
                    f_total -= self.score * SCORE_RMB_RATE
# score calc end

            break # while True
        self.total = f_total
        self.ext['calc_total'] = True
        return f_total

    def is_inquiry(self):
        js_cloth = self.clothes
        if self.comment != '':
            self.ext['inquiry'] = True
            return True
        if self.ext.get('immediate'):
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

    def cancel(self, admin=False):
        mo_user = self.own
        s_errmsg = self.ext.get('error')
# return user score
        if None == s_errmsg or '' == s_errmsg and self.score > 0:
            mo_user.score += self.score
        if admin:
            self.change_status(Bill.ADMIN_CANCEL)
        else:
            self.change_status(Bill.USER_CANCEL)

        self.save()
# remove order push
        a_orderqueue = OrderQueue.objects.filter(bill=self, status__lte=OrderQueue.TODO)
        for it_orderqueue in a_orderqueue:
            it_orderqueue.status = OrderQueue.NO_DO_BUT_DONE
            it_orderqueue.save()
# return coupon
        if self.ext.get('use_mycoupon'):
            try:
                mo_mycoupon = MyCoupon.objects.get(mcid=self.ext.get('use_mycoupon'))
                if mo_mycoupon.used:
                    mo_mycoupon.used = False
                    mo_mycoupon.save()
            except (MyCoupon.DoesNotExist) as e:
                self.add_error(e.__str__())
                self.save()
        if self.ext.get('payment') in ONLINE_PAYMENT and self.paid > 0:
            mo_re = Pingpp.create_refund(self)
            if None != mo_re:
                mo_ping_re = Pingpp_Refund.clone(mo_re)
        logging.info('bill[%s] cancel successfully' %(self.bid))
        return True

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
    name = models.CharField(max_length=255, verbose_name=u'代金券名称')
    create_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(verbose_name=u'开始时间')
    expire_time = models.DateTimeField(verbose_name=u'截止时间，如果有持续时间，则尽量设大截止时间')
# keep_time start at getting coupon,
# max(now, start_time) ~ min(now + keep_time, expire_time)
# this is timedelta type, start with start_time(see code)
    keep_time = models.DateTimeField(verbose_name=u'持续时间', \
        help_text=u'如果有则从开始时间算起，和截止时间比较取最近时间，否则和开始时间完全相同，对，我说的是包括时分秒')
# exp threshold user's exp must greater than this
    exp_thd = models.IntegerField(default=0, verbose_name=u'经验值阈值', \
        help_text=u'至少有这么多经验值的用户才能使用，分发会验证')
# cloth threshold this can be first category, bill must contain at least one
# cloth which cid equal cid_thd, null represent all clothes
    cid_thd = models.ForeignKey(Cloth, blank=True, null=True, verbose_name=u'适用衣物分类', \
        help_text=u'可以是一级分类，如果全场适用则不选')
# price threshold total price greater than this
    price_thd = models.FloatField(default=0, verbose_name=u'价格阈值', \
        help_text=u'所有该衣物分类下的所有衣物加起来的价格>=这个值')
# percent discount [0,100] like 10% off, percent discount will be calc before price
    percent_dst = models.IntegerField(default=0, verbose_name=u'折扣', \
        help_text=u'取值[0,100]，0表示不打折，20表示8折，以此类推')
# price discount minus price directly
    price_dst_low = models.IntegerField(default=0, verbose_name=u'价格减免下限')
    price_dst_upp = models.IntegerField(default=0, verbose_name=u'价格减免上限')
# global max use limit, 0 for no limit
    max_limit = models.IntegerField(default=0, verbose_name=u'最大拥有量', \
        help_text=u'最大该代金券数量，0表示无限量')
    use_code = models.BooleanField(default=False, verbose_name=u'是否可用代码兑换')
    code = models.CharField(max_length=12, default='', verbose_name=u'兑换代码', \
        help_text=u'自动生成')

    def __unicode__(self):
        return "%d(%s) code[%s]" %(self.coid, self.name, self.code)

    def is_valid(self):
        """ check coupon out of max_limit """
        if self.max_limit > 0:
            a_mycoupons = MyCoupon.objects.filter(coupon=self)
            if len(a_mycoupons) >= self.max_limit:
                logging.warning('coupon [%s] out of max_limit[%d/%d]' \
                    %(self.coid, len(a_mycoupons), self.max_limit))
                return False
        return True

# return mcid or 0
    def add_user(self, mo_user):
        if None == mo_user:
            return 0
        dt_now = dt.datetime.now()
        dt_delta = self.keep_time - self.start_time
        if not self.is_valid():
            return 0
# keep_time valid
        if dt_delta.total_seconds() > 0:
            dt_start_time = max(dt_now, self.start_time)
            dt_expire_time = min(dt_now+dt_delta, self.expire_time)
        else:
            dt_start_time = self.start_time
            dt_expire_time = self.expire_time
        import random
        if self.price_dst_low > self.price_dst_upp:
            logging.error('coupon price dst error low[%d] upp[%d]' %(self.price_dst_low, self.price_dst_upp))
        i_price_dst = random.choice(range(self.price_dst_low, self.price_dst_upp+1) or [0])
        mo_mycoupon = MyCoupon.objects.create(own=mo_user,\
            start_time=dt_start_time, expire_time=dt_expire_time,\
            price_thd=self.price_thd, percent_dst=self.percent_dst, \
            price_dst=i_price_dst, coupon=self)
        return mo_mycoupon.mcid

    @classmethod
    def gen_code(cls):
        import random
        chars = 'ABCEFGHJKPQRSTWXY13456789'
        return ''.join(random.sample(chars, 12))

    def save(self, *args, **kwargs):
        if self.use_code and (None == self.code or '' == self.code):
            self.code = Coupon.gen_code()
        super(self.__class__, self).save(*args, **kwargs)

class MyCoupon(models.Model):
    CAN_USE = 1
    NOUSED = 2
    USED_OR_EXPIRE = 3
    ALL = 9

    mcid = models.AutoField(primary_key=True, verbose_name=u'代金券id')
    own = models.ForeignKey('WCUser.User', db_index=True, verbose_name=u'用户id')
# use for coupon.max_limit
    coupon = models.ForeignKey(Coupon, default=None, blank=True, null=True, verbose_name=u'原代金券id')
    used = models.BooleanField(default=False, verbose_name=u'已用过标志')
    start_time = models.DateTimeField(default=dt.datetime(2014,1,1), verbose_name=u'开始时间')
    expire_time = models.DateTimeField(default=dt.datetime(2014,1,1), verbose_name=u'截止时间')
    cid_thd = models.ForeignKey(Cloth, blank=True, null=True, verbose_name=u'适用衣物分类', \
        help_text=u'可以是一级分类，如果全场适用则不选')
    price_thd = models.FloatField(default=0, verbose_name=u'价格阈值', \
        help_text=u'所有该衣物分类下的所有衣物加起来的价格>=这个值')
    percent_dst = models.IntegerField(default=0, verbose_name=u'折扣', \
        help_text=u'取值[0,100]，0表示不打折，20表示8折，以此类推')
    price_dst = models.FloatField(default=0, verbose_name=u'价格减免')
    ext = JSONField(default={}, verbose_name=u'扩展字段')
    status = 0

    def __unicode__(self):
        if None == self.cid_thd:
            s_cid_name = u'全场'
        else:
            s_cid_name = self.cid_thd.name
        return "%d([%s][%.0f,%s] -%.0f -%d%%) %s" % (self.mcid, self.own.name, self.price_thd, \
                        s_cid_name, self.price_dst, self.percent_dst, self.coupon)

    @classmethod
    def query_mycoupons(cls, mo_user, i_type):
        if None == mo_user:
            return None
        dt_now = dt.datetime.now()
        if MyCoupon.ALL == i_type:
            s_status = [MyCoupon.CAN_USE, MyCoupon.NOUSED, MyCoupon.USED_OR_EXPIRE]
        else:
            s_status = [i_type]
        a_ret_mycoupons = []
        for i_type in s_status:
            if MyCoupon.CAN_USE == i_type:
                a_mycoupons = MyCoupon.objects.filter(own=mo_user, used=False, \
                                start_time__lte = dt_now, expire_time__gt = dt_now)
            elif MyCoupon.NOUSED == i_type:
                a_mycoupons = MyCoupon.objects.filter(own=mo_user, used=False, \
                                start_time__gte = dt_now, expire_time__gt = dt_now)
            elif MyCoupon.USED_OR_EXPIRE == i_type:
                a_mycoupons = MyCoupon.objects.filter(Q(own=mo_user) & (Q(used=True) \
                                | Q(expire_time__lte = dt_now)))
            else:
                a_mycoupons = None
                logging.error('query_mycoupons type error [%d]' %(i_type))
            if None != a_mycoupons:
                a_mycoupons = a_mycoupons.order_by('used', 'start_time', 'expire_time', 'mcid')
                from WCBill.serializers import MyCouponSerializer
                for it_mycoupon in a_mycoupons:
                    # se_mycoupon = MyCouponSerializer(it_mycoupon)
                    # se_mycoupon.data['status'] = i_type
                    it_mycoupon.status = i_type
                    a_ret_mycoupons.append(it_mycoupon)
        return a_ret_mycoupons

    def get_status(self):
        dt_now = dt.datetime.now()
        if self.start_time <= dt_now and dt_now < self.expire_time:
            return MyCoupon.CAN_USE
        elif self.start_time >= dt_now and self.expire_time > dt_now:
            return MyCoupon.NOUSED
        elif self.used or self.expire_time <= dt_now:
            return MyCoupon.USED_OR_EXPIRE
        return 0

# return False or bill.total
    def is_vali_or_total(self, mo_bill, b_report_error=True):
        if None == mo_bill:
            return False
        if mo_bill.own != self.own:
            return False
        if self.used:
            return False
        self.status = self.get_status()
        if self.status != MyCoupon.CAN_USE:
            return False
        dt_now = dt.datetime.now()
        if dt_now < self.start_time or dt_now >= self.expire_time:
            return False
# fake bill just validate coupon
        t_bill = Bill(clothes=mo_bill.clothes)
        t_bill.ext['use_coupon'] = self.mcid
        t_bill.calc_total()
        if None != t_bill.ext.get('error') or None == t_bill.ext.get('use_coupon'):
            if b_report_error:
                logging.error(t_bill.ext)
            return False
        return t_bill.total

class Feedback(models.Model):
    fid = models.AutoField(primary_key=True)
    bill = models.ForeignKey(Bill, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField(default=5)
    content = models.CharField(max_length=1023)

    def __unicode__(self):
        s_ret = ''
        for i in range(self.rate):
            s_ret += u'★'
        s_ret += u' 评价[%s]' %(self.content)
        s_ret += u' 订单[%d]' %(self.bill_id)
        return s_ret

class Cart(Mass_Clothes):
    caid = models.AutoField(primary_key=True)
    own = models.ForeignKey(User, unique=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        s_name = ''
        s_name += '%d' %(self.caid)
        if self.own:
            if self.own.default_adr:
                s_name += '(%s)' %(self.own.default_adr.real_name)
            else:
                s_name += '(%s)' %(self.own.name)
        i_clothes_num = 0
        for it_cloth in self.clothes:
            i_clothes_num += int(it_cloth.get('number') or 0)
        s_name += u'[%d]件' %(i_clothes_num)
        return s_name

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
        a_new_clothes = []
        mo_cart.ext['last'] = []
        for it_cloth in mo_cart.clothes:
            if 'cid' in it_cloth and it_cloth['cid'] not in d_del_cloth:
                a_new_clothes.append(it_cloth)
            else:
                mo_cart.ext['last'].append(it_cloth)
        mo_cart.clothes = a_new_clothes
        mo_cart.save()
        return mo_cart.caid

class Pingpp():
# in parent directory
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    config = ConfigParser.ConfigParser()
    app_id = ''

    @classmethod
    def load_key(cls):
        with open(os.path.join(cls.conf_dir, 'pingpp.conf'), 'r') as rfdconf:
            cls.config.readfp(rfdconf)
            s_api_key = cls.config.get('common', 'api_key')
            s_app_id = cls.config.get('common', 'app_id')
        pingpp.api_key = s_api_key
        cls.app_id = s_app_id

# return ping charge object instead of Pingpp
    @classmethod
    def create_charge(cls, mo_bill, s_client_ip=None):
        cls.load_key()

        s_client_ip = s_client_ip or '127.0.0.1'
        try:
            mo_chr = pingpp.Charge.create(
                order_no=mo_bill.bid,
# price, unit is CNY fen
                amount=int(mo_bill.total * 100 + 0.5),
                app=dict(id=cls.app_id),
                channel=mo_bill.ext.get('payment'),
                currency='cny',
                client_ip=s_client_ip,
                subject=mo_bill.real_name,
                body=mo_bill.get_full_address(),
            )
        except (Exception) as e:
            logging.error('create charge failed %s' %(e))
            return None
        return mo_chr

    @classmethod
    def get_charge(cls, s_charge_id):
        cls.load_key()

        try:
            mo_chr = pingpp.Charge.retrieve(s_charge_id)
        except (Exception) as e:
            logging.error('get charge failed [%s]' %(e))
            mo_chr = None
        return mo_chr

    @classmethod
    def create_refund(cls, mo_bill):
        cls.load_key()

        try:
            mo_chr = pingpp.Charge.retrieve(Pingpp_Charge.objects.get(order_no=mo_bill.bid).id)
        except (Exception) as e:
            logging.error('no Pingpp_Charge order_no[%d]' %(mo_bill.bid))
            return None
        try:
            mo_re = mo_chr.refunds.create(description='%s' %(mo_bill.bid))
        except (Exception) as e:
            logging.error('create refund failed %s' %(e))
            return None
        logging.info('create refund successfully id[%s]' %(mo_re.id))
        return mo_re

class Pingpp_Abstract(models.Model):
    class Meta:
        abstract = True

    ext = JSONField(default={})

    @classmethod
    def convert_obj_dict(cls, mo_obj):
        """
        clone Pingpp_Obj from object(Charge, Refund) or dict(notify pass json),
        put exist fields in Pingpp_obj
        and save origin obj json in `ext` field
        """
        logging.debug(mo_obj)
        if None == mo_obj:
            return None
        d_ping_obj = {}
        if  type(mo_obj) in [pingpp.resource.Charge, pingpp.resource.Refund]:
            d_ping_obj['ext'] = mo_obj
            s_object = mo_obj.object
            for field in cls._meta.fields:
                s_fname = field.name
                if hasattr(mo_obj, s_fname):
                    d_ping_obj[s_fname] = getattr(mo_obj, s_fname)
        elif dict == type(mo_obj):
            d_ping_obj['ext'] = mo_obj
            s_object = mo_obj['object']
            for field in cls._meta.fields:
                s_fname = field.name
                if s_fname in mo_obj:
                    d_ping_obj[s_fname] = mo_obj[s_fname]
        else:
            logging.error('clone Pingpp_Obj type[%s] error' %(type(mo_obj)))
            return None
        return d_ping_obj

    @classmethod
    def clone(cls, mo_obj):
        d_ping_obj = cls.convert_obj_dict(mo_obj)
        logging.debug(d_ping_obj)
        try:
            mo_ping_obj, created = cls.objects.update_or_create(defaults=d_ping_obj, id=d_ping_obj['id'])
        except (Exception) as e:
# some attr missing
            logging.error('clone Pingpp_Obj error %s' %(e))
            mo_ping_obj = None
        return mo_ping_obj

class Pingpp_Charge(Pingpp_Abstract):
    id = models.CharField(max_length=48, primary_key=True)
    created = models.IntegerField()
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    channel = models.CharField(max_length=16)
    order_no = models.CharField(max_length=64)
    client_ip = models.IPAddressField()
# bill total price, unit is CNY fen
    amount = models.IntegerField(default=0)
    subject = models.CharField(max_length=32)
    body = models.CharField(max_length=128, null=True, blank=True)
    time_paid = models.IntegerField(null=True, blank=True)
    time_expire = models.IntegerField(null=True, blank=True)
    transaction_no = models.CharField(max_length=128, null=True, blank=True)
    failure_code = models.CharField(max_length=32, null=True, blank=True)
    failure_msg = models.CharField(max_length=1024, null=True, blank=True)

class Pingpp_Refund(Pingpp_Abstract):
    id = models.CharField(max_length=48, primary_key=True)
    created = models.IntegerField(null=True, blank=True)
    order_no = models.CharField(max_length=64)
# bill total price, unit is CNY fen
    amount = models.IntegerField(default=0)
    succeed = models.BooleanField(default=False)
    time_succeed = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=255)
    failure_code = models.CharField(max_length=32, null=True, blank=True)
    failure_msg = models.CharField(max_length=1024, null=True, blank=True)
    charge = models.ForeignKey('Pingpp_Charge')

    @classmethod
    def convert_obj_dict(cls, mo_obj):
        d_ping_obj = super(Pingpp_Refund, cls).convert_obj_dict(mo_obj)
# replace refund.charge to charge_id which is foreignkey
        if 'charge' in d_ping_obj:
            d_ping_obj['charge_id'] = d_ping_obj['charge']
            del d_ping_obj['charge']
        return d_ping_obj

