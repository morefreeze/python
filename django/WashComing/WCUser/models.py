# coding=utf-8
from django.forms import ValidationError
from django.db import models
from jsonfield import JSONField
from WCLogistics.models import Address
import base64
import hashlib

# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255)
    token = models.CharField(max_length=32)
    openauth = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    email = models.CharField(max_length=128,default='')
    default_adr = models.OneToOneField('WCLogistics.Address',null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_time = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    invited_uid = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.uid)

    @classmethod
    def create(cls, d_request):
        s_name = d_request.get('username')
        return cls(uid=None, name=s_name, token='')

    @classmethod
    def gen_token(cls, d_request):
        d_user_args = dict()
        d_user_args['username'] = d_request.get('username')
        d_user_args['password'] = d_request.get('password')
        d_user_args['secret'] = 'Keep It Simple, Stupid'
        s_user_args = ''
        sorted(d_user_args.items(), key=lambda e:e[0])
# generate string like 'username=123&password=abc'
        for k, v in d_user_args.items():
            s_user_args += '%s=%s&' %(k, v)
        s_user_args = s_user_args[:-1].encode('utf-8')
# generate token with md5(bash64())
        s_token = base64.b64encode(s_user_args)
        s_token = hashlib.md5(s_token).hexdigest().upper()
        return s_token

# if vali pass return User obj else return None
    @classmethod
    def vali_passwd(cls, d_request):
        s_token = cls.gen_token(d_request)
        s_name = d_request.get('username')
        try:
            mo_user = cls.objects.get(name=s_name)
            if mo_user.token != s_token:
                raise ValidationError('password does not match username')
        except (cls.DoesNotExist, ValidationError) as e:
            return None
        return mo_user

    @classmethod
    def get_user(cls, name, token):
        try:
            mo_user = cls.objects.get(name=name, token=token)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

    @staticmethod
    def gen_level(i_score):
        return 42

#=============User end

class Shop(models.Model):
    sid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255,default='')
    real_name = models.CharField(max_length=255,default='')
    provice = models.CharField(max_length=15,default='')
    city = models.CharField(max_length=63,default='')
    address = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    def __unicode__(self):
        return "%s(%d)" %(self.name, self.sid)
