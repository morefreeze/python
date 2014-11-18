#coding=utf-8
from WCLib.tests import *
from WCLib.serializers import *
from WCBill.models import Bill, Coupon, Feedback
from WCBill.serializers import BillSerializer, FeedbackSerializer
from WCCloth.models import Cloth
import datetime as dt

# Create your tests here.
class BillTest(TestCase):
    pass

class FeedbackTest(TestCase):
    username = 'unittest0@qq.com'
    passwd = 'abcdef'
    phone = '12345678901'
    token = ''

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
        self.assertJSONEqual(res.content, {'aid':1, 'errno':0})

# add cloth
        Cloth.objects.create(name='a', price=35)
        Cloth.objects.create(name='b', price=42)

        res = self.client.get(
            u'/bill/submit',
            {'username':self.username, 'token':self.token,
             'get_time_0':'2014-10-23 16:31:34', 'get_time_1':'2014-10-23 18:31:34',
             'return_time_0':'2014-10-26 16:31:34', 'return_time_1':'2014-10-26 18:31:34',
             'aid':1, 'clothes':'[{"price":35,"number":7,"cid":1},{"price":42,"number":12,"cid":2}]'
            })
        self.assertJSONEqual(res.content, {'bid':1, 'total':749.0, 'errno':0})


    def test_feedback(self):
        dt_now = dt.datetime.now()
        res = self.client.get(u'/bill/feedback', {'username':self.username, 'token':self.token,
                                                  'bid':1, 'rate':4, 'content':'feel good'})
        self.assertJSONEqual(res.content, {'errno':0})
        mo_fb = Feedback.objects.get(fid=1)
        se_fb = FeedbackSerializer(mo_fb)
        self.assertEqual(se_fb.data, {'fid':1, 'rate':4, 'bill':1, 'content':'feel good','create_time':dt_now.strftime(DATETIME_FORMAT)})

