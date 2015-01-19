# coding=utf-8
from WCLib.models import *
from django.forms import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
import django.contrib.auth.hashers as hasher
from django.template import loader, Context
import base64, hashlib, uuid
import datetime as dt
import json
import urllib, urllib2

# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True, verbose_name=u'用户id', help_text=u'')
    name = models.CharField(unique=True,max_length=255, verbose_name=u'用户名', \
        help_text=u'目前和手机号相同')
    token = models.CharField(max_length=255, verbose_name=u'用户token', \
        help_text=u'用户登陆凭据，由密码加密而来')
# qq$12345|wb$54321|
    third_uids = models.CharField(max_length=255,default='',blank=True, \
        verbose_name=u'第三方登陆用户名', help_text=u'格式为"qq$12345|wb$54321|"')
    third_token = models.CharField(max_length=255,default='',blank=True, \
        verbose_name=u'第三方登陆token', help_text=u'第三方最近一次登陆凭据')
    avatar = models.ImageField(default='', upload_to=get_avatar_filename,blank=True, \
        verbose_name=u'头像', help_text=u'')
    phone = models.CharField(max_length=12,default='',blank=True, \
        verbose_name=u'手机', help_text=u'')
    email = models.CharField(max_length=128,default='',blank=True, \
        verbose_name=u'邮箱', help_text=u'')
    default_adr = models.OneToOneField('WCLogistics.Address',null=True,blank=True, \
        verbose_name=u'默认收货地址', help_text=u'')
    create_time = models.DateTimeField(auto_now_add=True,blank=True, \
        verbose_name=u'注册时间', help_text=u'')
    last_time = models.DateTimeField(auto_now=True, verbose_name=u'上次操作时间', help_text=u'')
    score = models.IntegerField(default=0, verbose_name=u'积分', help_text=u'')
    exp = models.IntegerField(default=0, verbose_name=u'经验值', help_text=u'')
    invited = models.ForeignKey('self',null=True,default=None,blank=True, \
        verbose_name=u'被邀请用户', help_text=u'被邀请用户将会得到额外积分在该用户积分结算时')
    is_active = models.BooleanField(default=False, verbose_name=u'邮箱激活标志', help_text=u'')
    deleted = models.BooleanField(default=False, verbose_name=u'删除标志', help_text=u'')
    ext = JSONField(default={},blank=True, verbose_name=u'扩展字段', help_text=u'')

    def __unicode__(self):
        if None != self.default_adr:
            s_real_name = self.default_adr.real_name
        else:
            s_real_name = ''
        return "%d([%s] [%s])" %(self.uid, s_real_name, self.name)

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            mo_user = self.__class__.objects.get(uid=self.uid)
            s_old_avatar = mo_user.avatar.__str__()
            if self.avatar != mo_user.avatar:
                mo_user.avatar.delete(save=False)
        except:
            pass # when new photo then we do nothing, normal case
        super(self.__class__, self).save(*args, **kwargs)

    @classmethod
    def create(cls, d_request):
        s_phone = d_request.get('phone')
        s_name = s_phone
        return cls(uid=None, name=s_name, token='', phone=s_phone)

    @classmethod
    def gen_token(cls, s_passwd):
        s_token = hasher.make_password(s_passwd)
        return s_token

# if vali pass return User obj else return None
    @classmethod
    def vali_passwd(cls, d_request):
        s_name = d_request.get('username')
        try:
            mo_user = cls.objects.get(name=s_name, deleted=False)
            if not hasher.check_password(d_request.get('password'), mo_user.token):
                raise ValidationError('password does not match username')
        except (cls.DoesNotExist, ValidationError) as e:
            return None
        return mo_user

    @classmethod
    def get_user(cls, name, token, is_active=None):
        try:
            if None == is_active:
                mo_user = cls.objects.filter((Q(name=name) & Q(token=token))
                                             | (Q(third_uids__contains=name) & Q(third_token=token)),
                                             Q(deleted=False))[0]
            else:
                mo_user = cls.objects.filter((Q(name=name) & Q(token=token))
                                             | (Q(third_uids__contains=name) & Q(third_token=token)),
                                             Q(is_active=is_active),
                                             Q(deleted=False))[0]
        except (cls.DoesNotExist, IndexError) as e:
            return None
        return mo_user

    @classmethod
    def query_user(cls, name, deleted=None):
        try:
            if None == deleted:
                mo_user = cls.objects.get(name=name, deleted=False)
            else:
                mo_user = cls.objects.get(name=name, deleted=deleted)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

    @classmethod
    def query_email(cls, email, deleted=None):
        try:
            if None == deleted:
                mo_user = cls.objects.get(email=email)
            else:
                mo_user = cls.objects.get(email=email, deleted=False)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

    @staticmethod
    def gen_level(i_score):
        for it_lv in USER_LEVEL:
            if i_score >= it_lv['lower']:
                return it_lv['name']
        return NO_LEVEL

    def send_active(self, d_request):
        d_active = dict()
        d_active['time'] = dt.datetime.now().strftime('%Y%m%d %H:%M:%S')
        d_active['uuid'] = "%s" %(uuid.uuid4())
        s_token = hashlib.md5(
            json.dumps(d_active, sort_keys=True, separators=(',', ': '))
        ).hexdigest().upper()
        s_url = "http://" + d_request.get_host() + "/user/active?username=%s&active_token=%s" %(self.name, s_token)
        t_active = loader.get_template('active/send_active.html')
        c_active = Context({
            'username': self.name,
            'active_url': s_url,
        })
        self.ext['active_token'] = s_token
        self.ext['active_expire'] = (dt.datetime.now()+dt.timedelta(days=2))\
            .strftime('%Y%m%d %H:%M:%S')
        self.save()

        return t_active.render(c_active)

    def send_reset(self, d_request):
        d_active = dict()
        d_active['username'] = self.name
        d_active['time'] = dt.datetime.now().strftime('%Y%m%d %H:%M:%S')
        d_active['uuid'] = "%s" %(uuid.uuid4())
        s_token = hashlib.md5(
            json.dumps(d_active, sort_keys=True, separators=(',', ': '))
        ).hexdigest().upper()
        s_url = "http://" + d_request.get_host() + "/user/reset_password_confirm?username=%s&reset_token=%s" %(self.name, s_token)
        t_active = loader.get_template('reset/send_reset.html')
        c_active = Context({
            'email': self.name,
            'reset_url': s_url,
        })
        self.ext['reset_token'] = s_token
        self.ext['reset_expire'] = (dt.datetime.now()+dt.timedelta(days=1))\
            .strftime('%Y%m%d %H:%M:%S')
        self.save()

        return t_active.render(c_active)

    @classmethod
# return b_valid, s_third_name
# if b_valid == False then s_third_name is None
    def get_third_name(cls, s_tag, *args, **kwargs):
        if '' != s_tag:
            s_method_name = 'get_%s_third_name' %(s_tag)
            logging.debug(s_method_name)
            if hasattr(cls, s_method_name):
                logging.debug(getattr(cls, s_method_name))
                return getattr(cls, s_method_name)(*args, **kwargs)
        return False, None

    @classmethod
    def get_wb_third_name(cls, *args, **kwargs):
        s_url = 'https://api.weibo.com/2/users/show.json'
        d_data = {
            'uid':kwargs.get('third_uid'),
            'access_token':kwargs.get('access_token'),
        }
        try:
            req = urllib2.Request(s_url+'?'+urllib.urlencode(d_data))
            logging.debug(req.get_full_url())
            response = urllib2.urlopen(req)
            s_page = response.read()
            d_page = json.loads(s_page)
            if 'screen_name' in d_page:
                return True, d_page['screen_name']
            else:
                logging.error(d_page)
        except (Exception) as e:
            logging.error("%s" %(e.__str__()))
        return False, None

    @classmethod
    def get_qq_third_name(cls, *args, **kwargs):
        s_url = 'https://graph.qq.com/user/get_user_info'
        d_data = {
            'format':'json',
            'oauth_consumer_key':kwargs.get('oauth_consumer_key') or '1103449549',
            'openid':kwargs.get('third_uid'),
            'access_token':kwargs.get('access_token'),
        }
        try:
            req = urllib2.Request(s_url+'?'+urllib.urlencode(d_data))
            logging.debug(req.get_full_url())
            response = urllib2.urlopen(req)
            s_page = response.read()
            d_page = json.loads(s_page)
            if 'nickname' in d_page:
                return True, d_page['nickname']
            else:
                logging.error(d_page)
        except (Exception) as e:
            logging.error("%s" %(e.__str__()))
        return False, None

#=============User end

class Shop(models.Model):
    sid = models.AutoField(primary_key=True, verbose_name=u'店铺id', help_text=u'')
    name = models.CharField(unique=True,max_length=255,default='', \
        verbose_name=u'店铺名', help_text=u'采用缩写使用和物流对照')
    real_name = models.CharField(max_length=255,default='', verbose_name=u'店长姓名', help_text=u'')
    province = models.CharField(max_length=15,default='',choices=Province_Choice, \
        verbose_name=u'省', help_text=u'')
    city = models.CharField(max_length=63,default='',choices=City_Choice, \
        verbose_name=u'市', help_text=u'')
    area = models.CharField(max_length=15,default='',choices=Area_Choice, \
        verbose_name=u'区', help_text=u'')
    address = models.CharField(max_length=255,default='', verbose_name=u'店铺地址', help_text=u'')
    phone = models.CharField(max_length=12,default='', verbose_name=u'电话', help_text=u'')
# shop get clothes from logistics and return it
    byself = models.BooleanField(default=False, verbose_name=u'自取标志', \
        help_text=u'是否去物流站点自取')
    deleted = models.BooleanField(default=False, verbose_name=u'删除标志', help_text=u'')
    ext = JSONField(default={}, verbose_name=u'扩展字段', help_text=u'')

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.sid)

    def get_full_address(self):
        if 0 == len(self.province + self.city + self.area):
            s_separator = ''
        else:
            s_separator = ' '
        return self.province + self.city + self.area + " " + self.address

#============Shop end

class Feedback(models.Model):
    fid = models.AutoField(primary_key=True, verbose_name=u'用户反馈id', help_text=u'')
    own = models.ForeignKey(User, verbose_name=u'用户名', help_text=u'')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'反馈时间', help_text=u'')
    content = models.CharField(max_length=1023, verbose_name=u'反馈内容', help_text=u'')

    def __unicode__(self):
        return "%s [%s]" %(self.content, self.own)

"""
class ShopUser(AbstractUser):
    own_shop = models.IntegerField()

    def get_full_name(self):
        return self.own_shop

    def get_short_name(self):
        return self.own_shop

    def __unicode__(self):
        return self.own_shop

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    """
