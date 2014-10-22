# coding=utf-8
from django.forms import ValidationError
from django.db import models
from jsonfield import JSONField
import base64
import hashlib

# Create your models here.
class User(models.Model):
    uid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True,max_length=255)
    token = models.CharField(max_length=32)
    openauth = models.CharField(max_length=255)
    phone = models.CharField(max_length=11,default='')
    email = models.CharField(max_length=128,default='')
    create_time = models.DateTimeField(auto_now_add=True)
    last_time = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    invited_uid = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    @classmethod
    def create(cls, d_request):
        s_name = d_request.get('username')
        return cls(uid=None, name=s_name, token='')
# gen_token will assisn token field

    def gen_token(self, d_request):
        d_user_args = dict()
        d_user_args['username'] = self.name
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
    def vali_passwd(self, d_request):
        s_token = self.gen_token(d_request)
        s_name = self.name
        try:
            mo_user = self.__class__.objects.get(name=s_name)
            if mo_user.token != s_token:
                raise ValidationError('password does not match username')
        except (self.__class__.DoesNotExist, ValidationError) as e:
            return None
        return mo_user

    @staticmethod
    def gen_level(i_score):
        return 42
