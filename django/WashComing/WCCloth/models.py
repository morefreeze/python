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
    image = models.CharField(max_length=255,default='')
    detail = models.CharField(max_length=255)
    price = models.FloatField(default=0.)
    deleted = models.BooleanField(default=False)
    ext = JSONField(default={})

    def __unicode__(self):
        return "%s(%d)" % (self.name, self.is_leaf)

    @classmethod
    def create(cls, d_request):
        b_is_leaf = d_request.get('is_leaf')
        i_fa_cid = d_request.get('fa_cid')
        s_name = d_request.get('name')
        s_detail = d_request.get('detail')
        f_price = d_request.get('price')
        return cls(cid=None, fa_cid=i_fa_cid, name=s_name, detail=s_detail,
                  price=f_price)

    @classmethod
    def get_category(cls):
        """
        return first category
        """
        try:
            a_category = cls.objects.filter(fa_cid=0, deleted=False, is_leaf=False)
        except (cls.DoesNotExist) as e:
            return None
        return a_category

    @classmethod
    def get_cloth(cls, i_cid):
        try:
            mo_cloth = cls.objects.get(cid=i_cid, deleted=False, is_leaf=True)
        except (cls.DoesNotExist) as e:
            return None
        return mo_cloth
