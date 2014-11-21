# coding=utf-8
from WCLib.serializers import *
from WCBill.models import Bill, Feedback

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('bid', 'create_time', 'get_time_0', 'get_time_1', \
                  'return_time_0', 'return_time_1', \
                  'own', 'lg', 'address', 'real_name', 'phone', \
                  'status', 'deleted', \
                  'clothes', 'total', 'comment')

    def transform_address(self, obj, value):
        return obj.get_full_address()

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('fid', 'create_time', 'bill', 'rate', 'content')
    def transform_create_time(self, obj, value):
        return value.strftime(DATETIME_FORMAT)
