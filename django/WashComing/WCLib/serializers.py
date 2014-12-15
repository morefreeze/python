#encoding=utf-8
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
import json
import datetime as dt

FULL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT = "%Y%m%dT%H:%M:%S"
DATETIME_FORMAT_SHORT = "%m%d %H:%M"

