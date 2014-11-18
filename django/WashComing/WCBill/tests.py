#coding=utf-8
from WCLib.tests import *
from WCLib.serializers import *
from WCBill.models import Bill, Coupon, Feedback
from WCBill.serializers import BillSerializer, FeedbackSerializer
from WCCloth.models import Cloth
from WCLogistics.models import Address
import datetime as dt

# Create your tests here.
class BillTest(TestCase):
    pass

class FeedbackTest(TestCase):
    username = 'unittest0@qq.com'
    passwd = 'abcdef'
    phone = '12345678901'
    token = ''
    bid = 0

    def setUp(self):
# register
        res = self.client.get(u'/user/register', {'email':self.username, 'password':self.passwd,'phone':self.phone})
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
        i_aid = json.loads(res.content)['aid']
        self.assertJSONEqual(res.content, {'aid':i_aid, 'errno':0})

# add cloth
        c1 = Cloth.objects.create(name='a', price=35)
        c2 = Cloth.objects.create(name='b', price=42)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':'2014-10-23 16:31:34', 'get_time_1':'2014-10-23 18:31:34',
             'return_time_0':'2014-10-26 16:31:34', 'return_time_1':'2014-10-26 18:31:34',
             'aid':i_aid, 'clothes':'[{"price":35,"number":7,"cid":%d},{"price":42,"number":12,"cid":%d}]' %(c1.cid, c2.cid)
            })
        self.bid = json.loads(res.content)['bid']
        self.assertJSONEqual(res.content, {'bid':self.bid, 'total':749.0, 'errno':0})

    def test_feedback(self):
        dt_now = dt.datetime.now()
        res = self.client.get(u'/bill/feedback', {'username':self.username, 'token':self.token,
                                                  'bid':self.bid, 'rate':4, 'content':'feel good'})
        i_fid = json.loads(res.content)['fid']
        mo_fb = Feedback.objects.get(fid=i_fid)
        se_fb = FeedbackSerializer(mo_fb)
        self.assertEqual(se_fb.data, {'fid':i_fid, 'rate':4, 'bill':1, 'content':'feel good','create_time':dt_now.strftime(DATETIME_FORMAT)})

    def test_get_feedback(self):
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

