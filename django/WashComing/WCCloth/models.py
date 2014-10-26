# coding=utf-8
from django.forms import ValidationError
from django.db import models
from jsonfield import JSONField
import base64
import hashlib

# Create your models here.
"""
cloth tree, include category which is branch,
cloth is leaf
"""
class Cloth(models.Model):
    cid = models.AutoField(primary_key=True)
    is_leaf = models.BooleanField(default=True)
    fa_cid = models.IntegerField(default=0)
    name = models.CharField(unique=True,max_length=32)
    detail = models.CharField(max_length=255)
    price = models.FloatField()
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    @classmethod
    def create(cls, d_request):
        b_is_leaf = d_request.get('is_leaf')
        i_fa_cid = d_request.get('fa_cid')
        s_name = d_request.get('name')
        s_detail = d_request.get('detail')
        f_price = d_request.get('price')
        return cls(cid=None, fa_cid=i_fa_cid, name=s_name, detail=s_detail,
                  price=f_price)
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

# if vali pass return Cloth obj else return None
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

    @classmethod
    def get_category(cls):
        """
        return first category
        """
        try:
            a_category = cls.objects.filter(fa_cid=0, deleted=False, is_leaf=False)
        except (cls.DoesNotExist) as e:
            return None

    @classmethod
    def get_cloth(cls, name):
        try:
            mo_user = cls.objects.get(name=name, token=token)
        except (cls.DoesNotExist) as e:
            return None
        return mo_user

