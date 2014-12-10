from django.db import models
from WCLib.models import *
from django.db.models import Max
from django.conf import settings
import shutil

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

    def save(self, *args, **kwargs):
        b_new_apk = False
        i_ver_code = self.__class__.objects.all().aggregate(Max('ver_code'))['ver_code__max']
        if None == i_ver_code or i_ver_code < self.ver_code:
            b_new_apk = True
        super(self.__class__, self).save(*args, **kwargs)
        if b_new_apk:
            s_file = os.path.join(settings.MEDIA_ROOT, self.file.__str__())
            s_latest_file = get_android_latest_apk()
            shutil.copyfile(s_file, s_latest_file)

    @classmethod
    def get_newest_version(cls):
        i_ver_code = cls.objects.all().aggregate(Max('ver_code'))['ver_code__max']
        if None == i_ver_code:
            return None
        mo_android = cls.objects.get(ver_code=i_ver_code)
        return mo_android

