# coding=utf-8
from WCLib.serializers import *
from WCUser.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'name', 'token', 'third_token', 'avatar', 'last_time', \
                  'score', 'exp', 'phone', 'email', 'is_active')
    def transform_last_time(self, obj, value):
        return value.strftime(DATETIME_FORMAT)

    def transform_name(self, obj, value):
        if '$' in value:
            tmp, value = value.split('$')
        return value

