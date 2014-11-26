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
    name = models.CharField(max_length=32)
    image = models.ImageField(default='',blank=True)
    detail = models.CharField(max_length=255,default='',blank=True)
    price = models.FloatField(default=0.)
# show weight, bigger show first
    weight = models.IntegerField(default=0)
    ext = JSONField(default={},blank=True)

    def __unicode__(self):
        return "%s(%d %d)" % (self.name, self.cid, self.price)

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
            a_category = cls.objects.filter(fa_cid=0, is_leaf=False).order_by('-weight', 'cid')
        except (cls.DoesNotExist) as e:
            return None
        return a_category

    @classmethod
    def get_cloth(cls, i_cid, is_leaf=None):
        try:
            if None == is_leaf:
                mo_cloth = cls.objects.get(cid=i_cid)
            else:
                mo_cloth = cls.objects.get(cid=i_cid, is_leaf=is_leaf)
        except (cls.DoesNotExist) as e:
            return None
        return mo_cloth

