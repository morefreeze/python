# coding=utf-8
from WCLib.serializers import *
#from WCCloth.models import Cloth

class LaundrySerializer(serializers.ModelSerializer):
    pass
    """
    third_bind = serializers.CharField(source='third_uids')

    class Meta:
        model = Cloth
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
    """
