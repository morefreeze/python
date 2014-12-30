# coding=utf-8
from WCLib.serializers import *
from WCBill.models import Bill, Feedback, MyCoupon

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('bid', 'create_time', 'get_time_0', 'get_time_1', \
                  'return_time_0', 'return_time_1', \
                  'own', 'lg', 'address', 'real_name', 'phone', \
                  'status', 'deleted', 'score', \
                  'clothes', 'total', 'comment', 'ext')

    def transform_address(self, obj, value):
        return obj.get_full_address()

    def transform_status(self, obj, value):
        return value

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('fid', 'create_time', 'bill', 'rate', 'content')
    def transform_create_time(self, obj, value):
        return value.strftime(DATETIME_FORMAT)

class MyCouponSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='cid_thd')
    price_threshold = serializers.CharField(source='price_thd')
    price_discount = serializers.FloatField(source='price_dst')
    percent_discount = serializers.IntegerField(source='percent_dst')
    status = serializers.IntegerField(source='status')

    class Meta:
        model = MyCoupon
        fields = ('mcid', 'own', 'start_time', 'expire_time', 'price_threshold', 'price_discount', \
                 'percent_discount', 'used', 'category', 'status')

    def transform_status(self, obj, value):
        if None != value:
            return value
        return 0

    def transform_category(self, obj, value):
        if None == value:
            return u'全场'
        return obj.cid_thd.name

    def transform_expire_time(self, obj, value):
        return value - dt.timedelta(seconds=1)
