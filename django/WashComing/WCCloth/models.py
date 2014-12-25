# coding=utf-8
from django.forms import ValidationError
from django.db import models
from jsonfield import JSONField
from WCLib.models import *
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
    fa_cid = models.ForeignKey('self', null=True,default=None,blank=True)
    name = models.CharField(max_length=32)
    image = models.ImageField(default='',blank=True,upload_to=get_cloth_filename)
    image_hidden = models.ImageField(default='',blank=True,upload_to=get_cloth_filename)
    detail = models.CharField(max_length=255,default='',blank=True)
    price = models.FloatField(default=0.)
# show weight, bigger show first
    weight = models.IntegerField(default=0)
    ext = JSONField(default={},blank=True)

    def __unicode__(self):
        return "%s(%d %.2f)" % (self.get_name(), self.cid, self.price)

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            mo_cloth = self.__class__.objects.get(cid=self.cid)
            s_old_image = mo_cloth.image.__str__()
            if self.image != mo_cloth.image:
                mo_cloth.image.delete(save=False)
# replace other model with same image
                if '' != s_old_image:
                    a_clothes = Cloth.objects.filter(image=s_old_image)
                    for it_cloth in a_clothes:
                        it_cloth.image = self.image
                        super(self.__class__, it_cloth).save(*args, **kwargs)
        except:
            pass # when new photo then we do nothing, normal case
        super(self.__class__, self).save(*args, **kwargs)

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
            a_category = cls.objects.filter(fa_cid=None, is_leaf=False).order_by('-weight', 'cid')
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

    @classmethod
    def is_ancestor(cls, i_ancestor, i_child):
        try:
            mo_ancestor = cls.objects.get(cid=i_ancestor)
            mo_child = cls.objects.get(cid=i_child)
            if None == mo_ancestor:
                return False
            for i in range(10):
                if None == mo_child:
                    break
                if None != mo_child.fa_cid and mo_ancestor.cid == mo_child.fa_cid.cid:
                    return True
                mo_child = mo_child.fa_cid
        except (cls.DoesNotExist) as e:
            return False

    def get_name(self):
        try:
            if self.fa_cid:
                mo_fa_cloth = self.fa_cid
# self is third category cloth
                if mo_fa_cloth.fa_cid:
                    return "%s_%s" % (mo_fa_cloth.name, self.name)
            return "%s" % (self.name)
        except Exception as e:
            return "NULL_%s" % (self.name)

