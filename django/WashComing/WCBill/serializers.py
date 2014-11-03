# coding=utf-8
from rest_framework import serializers
from WCBill.models import Bill

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('bid', 'create_time', 'get_time_0', 'get_time_1', \
                  'return_time_0', 'return_time_1', \
                  'own', 'lg', 'adr', 'status', 'deleted', \
                 'clothes')
