#coding=utf-8
from WCLib.tests import *
from WCLib.serializers import *
from WCBill.models import Bill, Coupon, Feedback, Cart
from WCBill.serializers import BillSerializer, FeedbackSerializer
from WCCloth.models import Cloth
from WCLogistics.models import Address
import datetime as dt

# Create your tests here.
class BillBaseTest(TestCase):
    username = '12345678901'
    passwd = 'abcdef'
    phone = '12345678901'
    token = ''
    bid = 0
    aid = 0
    get_time_0 = dt.datetime.now() + dt.timedelta(days=1)
    get_time_1 = get_time_0 + dt.timedelta(hours=3)
    return_time_0 = get_time_0 + dt.timedelta(days=4)
    return_time_1 = return_time_0 + dt.timedelta(hours=3)
    clothes = ''

    def setUp(self):
# register
        res = self.client.get(u'/user/register', {'password':self.passwd,'phone':self.phone})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)
        self.token = s_token

# add address
        res = self.client.get(
            u'/address/add',
            {'username':self.username, 'token':self.token,
             'real_name':'unittest', 'phone':self.phone,
             'province':'北京', 'city':'北京市', 'area':'海淀区',
             'address':'keshi',
             'set_default':1
            })
        self.aid = json.loads(res.content)['aid']
        self.assertJSONEqual(res.content, {'aid':self.aid, 'errno':0})

# add cloth
        c1 = Cloth.objects.create(name='a', price=35)
        c2 = Cloth.objects.create(name='b', price=42)
        self.clothes = '[{"price":35,"name":"a","number":7,"cid":%d,"image":""},{"price":42,"name":"b","number":12,"cid":%d,"image":""}]' \
                %(c1.cid, c2.cid)

class BillTest(BillBaseTest):

    def test_submit(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.bid = json.loads(res.content)['bid']
        self.assertJSONEqual(res.content, {'bid':self.bid, 'total':749.0, 'errno':0})

    def test_submit_time_logic_wrong(self):
# before now
        s_get_time_0 = (self.get_time_0 - dt.timedelta(days=2)).strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = (self.get_time_0 + dt.timedelta(hours=3)).strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg':'get_time error'})
# get_time_1 before get_time_0
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = (self.get_time_0 - dt.timedelta(hours=3)).strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg':'get_time error'})
# return_time_0 before get_time_1+96hrs
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = (self.return_time_0 - dt.timedelta(hours=3)).strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg':'return_time error'})
# return_time_1 before return_time_0
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = (self.return_time_0 - dt.timedelta(hours=3)).strftime(FULL_DATETIME_FORMAT)
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg':'return_time error'})

    def test_submit_wrong_address(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        i_aid = 9999
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':i_aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg':'address error'})

    def test_submit_lost_time(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

# lost get_time_0
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg': {'get_time_0': ['This field is required.']}})

# lost get_time_1
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg': {'get_time_1': ['This field is required.']}})

# lost return_time_0
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg': {'return_time_0': ['This field is required.']}})

# lost get_time_0
        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.assertJSONEqual(res.content, {'errmsg': {'return_time_1': ['This field is required.']}})

class FeedbackTest(BillBaseTest):

    def test_feedback(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.bid = json.loads(res.content)['bid']
        self.assertJSONEqual(res.content, {'bid':self.bid, 'total':749.0, 'errno':0})

        mo_bill = Bill.objects.get(bid=self.bid)
        mo_bill.status = Bill.NEED_FEEDBACK
        mo_bill.save()
        dt_now = dt.datetime.now()
        res = self.client.get(u'/bill/feedback', {'username':self.username, 'token':self.token,
                                                  'bid':self.bid, 'rate':4, 'content':'feel good'})
        i_fid = json.loads(res.content)['fid']
        mo_fb = Feedback.objects.get(fid=i_fid)
        se_fb = FeedbackSerializer(mo_fb)
        self.assertEqual(se_fb.data, {'fid':i_fid, 'rate':4, 'bill':self.bid, 'content':'feel good','create_time':dt_now.strftime(DATETIME_FORMAT)})

    def test_get_feedback(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.bid = json.loads(res.content)['bid']
        self.assertJSONEqual(res.content, {'bid':self.bid, 'total':749.0, 'errno':0})

        mo_bill = Bill.objects.get(bid=self.bid)
        mo_bill.status = Bill.NEED_FEEDBACK
        mo_bill.save()
        dt_now = dt.datetime.now()
        res = self.client.get(u'/bill/feedback', {'username':self.username, 'token':self.token,
                                                  'bid':self.bid, 'rate':5, 'content':'feel good too'})
        i_fid = json.loads(res.content)['fid']
        self.assertJSONEqual(res.content, {'fid':i_fid, 'errno':0})
        mo_fb = Feedback.objects.get(bill_id=self.bid)
        se_fb = FeedbackSerializer(mo_fb)
        se_fb.data['errno'] = 0
        res = self.client.get(u'/bill/get_feedback', {'username':self.username, 'token':self.token,
                                                      'bid':self.bid})
        self.assertEqual(se_fb.data, json.loads(res.content))

    def test_feedback_wrong_status(self):
        s_get_time_0 = self.get_time_0.strftime(FULL_DATETIME_FORMAT)
        s_get_time_1 = self.get_time_1.strftime(FULL_DATETIME_FORMAT)
        s_return_time_0 = self.return_time_0.strftime(FULL_DATETIME_FORMAT)
        s_return_time_1 = self.return_time_1.strftime(FULL_DATETIME_FORMAT)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':s_get_time_0, 'get_time_1':s_get_time_1,
             'return_time_0':s_return_time_0, 'return_time_1':s_return_time_1,
             'aid':self.aid, 'clothes':self.clothes
            })
        self.bid = json.loads(res.content)['bid']
        self.assertJSONEqual(res.content, {'bid':self.bid, 'total':749.0, 'errno':0})

# status != NEED_FEEDBACK
        for it_status in [Bill.READY, Bill.CONFIRMING, Bill.WAITTING_GET, \
                          Bill.GETTING, Bill.WASHING, Bill.RETURNNING, Bill.DONE, \
                         Bill.USER_CANCEL, Bill.ERROR]:
            mo_bill = Bill.objects.get(bid=self.bid)
            mo_bill.status = it_status
            mo_bill.save()
            res = self.client.get(u'/bill/feedback', {'username':self.username, 'token':self.token,
                                                      'bid':self.bid, 'rate':1, 'content':'can not feedback'})
            self.assertJSONEqual(res.content, {"errmsg": "bill do not need feedback"})

class CartTest(BillBaseTest):

    def test_cart(self):
# submit cart
        res = self.client.get(u'/cart/submit', {'username':self.username, 'token':self.token,
            'clothes':self.clothes,})
        i_caid = json.loads(res.content)['caid']
        self.assertJSONEqual(res.content, {'caid':i_caid, 'errno':0})
# list cart
        res = self.client.get(u'/cart/list', {'username':self.username, 'token':self.token,})
        self.assertJSONEqual(res.content, {'data':json.loads(self.clothes), 'clothes':json.loads(self.clothes), 'errno':0})

