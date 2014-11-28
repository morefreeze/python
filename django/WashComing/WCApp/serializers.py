# coding=utf-8
from WCLib.serializers import *
from WCApp.models import Android

class AndroidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Android
