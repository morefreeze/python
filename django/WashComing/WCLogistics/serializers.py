from rest_framework import serializers
from WCLogistics.models import RFD, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('aid', 'own', 'provice', 'city', 'area', 'address', 'real_name', 'phone')
