# coding=utf-8
from WCLib.serializers import *
from WCUser.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'name', 'token', 'last_time', 'score', 'exp', 'phone', \
                  'email', 'is_active')
    def transform_last_time(self, obj, value):
        return value.strftime(DATETIME_FORMAT)
