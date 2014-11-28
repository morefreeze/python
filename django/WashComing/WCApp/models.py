from django.db import models
from WCLib.models import *

# Create your models here.
class Android(models.Model):
    ver_code = models.IntegerField(primary_key=True)
    file = models.FileField(default='',blank=True,upload_to=get_android_apk)
    # full version info, e.g.:1.2.3.0
    ver_str = models.CharField(max_length=31)
    # update message, what fix, new feature
    update_msg = models.CharField(max_length=4095)

    def __unicode__(self):
        return "%d(v%s)" %(self.ver_code, self.ver_str)
