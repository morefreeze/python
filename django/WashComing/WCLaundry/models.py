# coding=utf-8
from WCLib.models import *
from django.forms import ValidationError
from django.db import models
from django.db.models import Q
import django.contrib.auth.hashers as hasher
from django.template import loader, Context
import base64, hashlib, uuid
import datetime as dt
import json
import urllib, urllib2

# Create your models here.
class BaseFakeModel(models.Model):
    pass

class QueryBill(BaseFakeModel):
    class Meta:
        proxy = True

class SendBill(BaseFakeModel):
    class Meta:
        proxy = True

