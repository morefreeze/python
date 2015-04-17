import os
import django
import sys

pwd = os.path.dirname(os.path.abspath(__file__))
fa_pwd = os.path.abspath(os.path.join(pwd, '..'))
sys.path.append(fa_pwd)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from book.models import C
c=C.objects.get(pk=2)
#print c.ext, c.t, c.e
#print type(c.ext), #type(c.t), type(c.e)
#print c.ext['a']
print c.js
