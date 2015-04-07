# coding=utf-8
from WCLib.serializers import *
from WCUser.models import User, Shop

class UserSerializer(serializers.ModelSerializer):
    third_bind = serializers.CharField(source='third_uids')

    class Meta:
        model = User
        fields = ('uid', 'name', 'token', 'third_token', 'avatar', 'last_time', \
                  'score', 'exp', 'phone', 'email', 'is_active', 'third_bind', )

    def transform_last_time(self, obj, value):
        return value.strftime(DATETIME_FORMAT)

    def transform_name(self, obj, value):
        if '$' in value:
            tmp, value = value.split('$')
        return value

    def transform_third_bind(self, obj, value):
        a_ret = []
        for it_third in value.split('|'):
            if '$' in it_third:
                a_ret.append(it_third[:it_third.find('$')])
        return a_ret

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('sid', 'name', 'rfd_name', 'real_name', 'phone', 'address', )

