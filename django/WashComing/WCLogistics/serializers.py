from rest_framework import serializers
from WCLogistics.models import Map, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('aid', 'own_id', 'provice', 'city', 'address', 'real_name')
