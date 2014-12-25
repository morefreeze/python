# coding=utf-8
from WCLib.models import *
from django.forms import ValidationError
from django.db import models
from django.db.models import Q
import django.contrib.auth.hashers as hasher
from django.template import loader, Context
import base64, hashlib, uuid
import datetime as dt
import json

# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255)
    token = models.CharField(max_length=255)
# qq$12345|wb$54321|
    third_uids = models.CharField(max_length=255,default='',blank=True)
    third_token = models.CharField(max_length=255,default='',blank=True)
    avatar = models.ImageField(default='', upload_to=get_avatar_filename,blank=True)
    phone = models.CharField(max_length=12,default='',blank=True)
    email = models.CharField(max_length=128,default='',blank=True)
    default_adr = models.OneToOneField('WCLogistics.Address',null=True,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,blank=True)
    last_time = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    invited = models.ForeignKey('self',null=True,default=None,blank=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={},blank=True)

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
                mo_user = cls.objects.filter(Q(name=name),
                                             Q(token=token) | Q(third_token=token),
                                             Q(deleted=False))[0]
            else:
                mo_user = cls.objects.filter(Q(name=name),
                                             Q(token=token) | Q(third_token=token),
                                             Q(is_active=is_active),
                                             Q(deleted=False))[0]
        except (cls.DoesNotExist, IndexError) as e:
            return None
        return mo_user

    @classmethod
    def query_user(cls, name, deleted=None):
        try:
            if None == deleted:
                mo_user = cls.objects.get(name=name)
            else:
                mo_user = cls.objects.get(name=name, deleted=False)
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
        d_active['username'] = self.name
        d_active['time'] = dt.datetime.now().strftime('%Y%m%d %H:%M:%S')
        d_active['uuid'] = "%s" %(uuid.uuid4())
        s_token = hashlib.md5(
            json.dumps(d_active, sort_keys=True, separators=(',', ': '))
        ).hexdigest().upper()
        s_url = "http://" + d_request.get_host() + "/user/active?username=%s&active_token=%s" %(self.name, s_token)
        t_active = loader.get_template('active/send_active.html')
        c_active = Context({
            'email': self.name,
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

#=============User end

class Shop(models.Model):
    sid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255,default='')
    real_name = models.CharField(max_length=255,default='')
    province = models.CharField(max_length=15,default='',choices=Province_Choice)
    city = models.CharField(max_length=63,default='',choices=City_Choice)
    area = models.CharField(max_length=15,default='',choices=Area_Choice)
    address = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

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
    fid = models.AutoField(primary_key=True)
    own = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=1023)

