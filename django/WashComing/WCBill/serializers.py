# coding=utf-8
from rest_framework import serializers
from WCBill.models import Bill

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('bid', 'create_time', 'get_time', 'return_time', \
                  'own', 'lg', 'adr', 'status', 'deleted', \
                 'clothes')
