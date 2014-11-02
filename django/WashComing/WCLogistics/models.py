from django.db import models

# Create your models here.
class RFD(models.Model):
    lid = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)
    get_way_no = models.IntegerField(default=0)
    get_form_no = models.IntegerField(default=0)
    get_message = models.CharField(max_length=255,default='')
    return_way_no = models.IntegerField(default=0)
    return_form_no = models.IntegerField(default=0)
    return_message = models.CharField(max_length=255,default='')

    def rfd_ImportOrders(self):
        pass

    def gen_get_bill(self, mo_user, mo_shop):
        [self.get_way_no, self.get_form_no] = rfd_ImportOrders()

class Address(models.Model):
    aid = models.AutoField(primary_key=True)
    own = models.ForeignKey('WCUser.User')
    real_name = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    provice = models.CharField(max_length=15,default='')
    city = models.CharField(max_length=63,default='')
    address = models.CharField(max_length=255,default='')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%d(%s)" % (self.aid, self.real_name)

    @classmethod
    def create(cls, mo_user, d_data):
        return cls(aid=None,own=mo_user, real_name=d_data.get('real_name'), \
                               provice=d_data.get('provice'),city=d_data.get('city'), \
                            phone=d_data.get('phone'), address=d_data.get('address') )

    @classmethod
    def get_adr(cls, own_id, aid, deleted=False):
        try:
            mo_adr = cls.objects.get(own_id=own_id, aid=aid, deleted=deleted)
        except (cls.DoesNotExist) as e:
            return None
        return mo_adr
