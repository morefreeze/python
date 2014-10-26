from django.db import models
from jsonfield import JSONField
from WCUser.models import User
from WCLogistics.models import Map, Address

# Create your models here.
class Bill(models.Model):
    bid = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)
    get_time = models.DateTimeField()
    return_time = models.DateTimeField()
    own = models.ForeignKey(User) # own_id in db
    lg = models.ForeignKey(Map,null=True) # lg_id in db
    adr = models.ForeignKey(Address) # adr_id in db
    status = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    clothes = JSONField(default=None)
    ext = JSONField(default=None)

    @classmethod
    def get_bill(cls, own_id, bid):
        try:
            mo_bill = cls.objects.get(own_id=own_id, bid=bid)
        except (cls.DoesNotExist) as e:
            return None
        return mo_bill

    @classmethod
    def get_bills(cls, own_id, pn=1, deleted=0, rn=10):
        l_bill = cls.objects.filter(own_id=own_id)[(pn-1)*rn:pn*rn]
        return l_bill
