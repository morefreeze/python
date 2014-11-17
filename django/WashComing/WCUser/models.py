# coding=utf-8
from django.forms import ValidationError
from django.db import models
from jsonfield import JSONField
from WCLogistics.models import Address
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
    openauth = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    email = models.CharField(max_length=128,default='')
    default_adr = models.OneToOneField('WCLogistics.Address',null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_time = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    invited = models.ForeignKey('self')
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.uid)

    @classmethod
    def create(cls, d_request):
        s_email = d_request.get('email')
        s_name = s_email
        return cls(uid=None, name=s_name, token='', email=s_email)

    @classmethod
    def gen_token(cls, d_request):
        s_token = hasher.make_password(d_request.get('password'))
        return s_token

# if vali pass return User obj else return None
    @classmethod
    def vali_passwd(cls, d_request):
        s_name = d_request.get('username')
        try:
            mo_user = cls.objects.get(name=s_name)
            if not hasher.check_password(d_request.get('password'), mo_user.token):
                raise ValidationError('password does not match username')
        except (cls.DoesNotExist, ValidationError) as e:
            return None
        return mo_user

    @classmethod
    def get_user(cls, name, token, is_active=True):
        try:
            mo_user = cls.objects.get(name=name, token=token, is_active=is_active)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

    @classmethod
    def query_user(cls, name):
        try:
            mo_user = cls.objects.get(name=name)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

    @staticmethod
    def gen_level(i_score):
        return 42

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

#=============User end

class Shop(models.Model):
    sid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255,default='')
    real_name = models.CharField(max_length=255,default='')
    province = models.CharField(max_length=15,default='')
    city = models.CharField(max_length=63,default='')
    address = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.sid)
