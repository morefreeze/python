#encoding=utf-8
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
import json
import datetime as dt

DATETIME_FORMAT = "%Y%m%dT%H:%M:%S"
