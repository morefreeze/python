import os
import django
import sys

pwd = os.path.dirname(os.path.abspath(__file__))
fa_pwd = os.path.abspath(os.path.join(pwd, '..'))
sys.path.append(fa_pwd)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lolking.settings")
django.setup()

