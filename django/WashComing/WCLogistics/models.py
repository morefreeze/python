from django.db import models

# Create your models here.
# todo: rename
class Map(models.Model):
    lid = models.AutoField(primary_key=True)

class Address(models.Model):
    aid = models.AutoField(primary_key=True)
    own = models.ForeignKey('WCUser.User')
    real_name = models.CharField(max_length=255,default='')
    provice = models.CharField(max_length=15,default='')
    city = models.CharField(max_length=63,default='')
    address = models.CharField(max_length=255,default='')
    deleted = models.BooleanField(default=False)

    @classmethod
    def create(cls, mo_user, d_data):
        return cls(aid=None,own=mo_user, real_name=d_data.get('real_name'), \
                               provice=d_data.get('provice'),city=d_data.get('city'), \
                            address=d_data.get('address') )

    @classmethod
    def get_adr(cls, own_id, aid, deleted=False):
        try:
            mo_adr = cls.objects.get(own_id=own_id, aid=aid, deleted=deleted)
        except (cls.DoesNotExist) as e:
            return None
        return mo_adr
