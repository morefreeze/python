# coding=utf-8
from WCLib.serializers import *
from WCBill.models import Bill, Feedback, MyCoupon

class BillSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop')
    get_order = serializers.CharField(source='lg')
    return_order = serializers.CharField(source='lg')
    feedback = serializers.CharField(source='lg')
    class Meta:
        model = Bill
        fields = ('bid', 'create_time', 'get_time_0', 'get_time_1', \
                  'return_time_0', 'return_time_1', \
                  'own', 'lg', 'get_order', 'return_order', 'address', 'real_name', 'phone', \
                  'status', 'deleted', 'score', 'shop', 'shop_name', 'shop_comment', \
                  'clothes', 'total', 'paid', 'comment', 'feedback', 'ext')

    def transform_address(self, obj, value):
        return obj.get_full_address()

    def transform_status(self, obj, value):
        return value

    def transform_shop_name(self, obj, value):
        if None == obj.shop:
            return u'（暂无）'
        return obj.shop.name

    def transform_get_order(self, obj, value):
        if None == obj.lg:
            return ''
        return obj.lg.get_order_no

    def transform_return_order(self, obj, value):
        if None == obj.lg:
            return ''
        return obj.lg.return_order_no

    def transform_feedback(self, obj, value):
        try:
            mo_fb = Feedback.objects.get(bill=obj)
        except (Exception) as e:
            return ''
        return mo_fb.content

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
        return obj.get_status()

    def transform_category(self, obj, value):
        if None == value:
            return u'全场'
        return obj.cid_thd.name

    def transform_expire_time(self, obj, value):
        return value - dt.timedelta(seconds=1)
