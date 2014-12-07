# coding=utf-8
from WCLib.tests import *
from WCUser.models import User, Feedback
from WCUser.serializers import UserSerializer

# Create your tests here.
class UserTest(TestCase):
    def test_register(self):
        res = self.client.get(u'/user/register', {'phone':'13345678900', 'password':'abcdef',})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_dup(self):
        self.client.get(u'/user/register', {'phone':'13345678901','password':'abcdef',})
        res = self.client.get(u'/user/register', {'phone':'13345678901','password':'abcdef',})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": "username has been registered"})

    def test_login(self):
        self.client.get(u'/user/register',{'phone':'13345678902','password':'abcdef',})
        res = self.client.get(u'/user/login',{'username':'13345678902','password':'abcdef'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_miss_field(self):
        res = self.client.get(u'/user/register',{'password':'abcdef',})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"phone": ["This field is required."]}})

        res = self.client.get(u'/user/register',{'phone':'13345678903',})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"password": ["This field is required."]}})

        res = self.client.get(u'/user/register',{'phone':'13345678903','password':'abcdef',})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_invite(self):
        self.client.get(u'/user/register',{'phone':'13345678904','password':'abcdef',})
        res = self.client.get(u'/user/register',{'phone':'13345678905','password':'abcdef','invited_username':'13345678904'})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678905')
        mo_inv_user = mo_user.invited
        self.assertEqual(mo_inv_user.name, '13345678904')

    def test_register_invite_nouser(self):
        res = self.client.get(u'/user/register',{'phone':'13345678906','password':'abcdef','invited_username':'NoThisUser'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':"invited user[NoThisUser] not found"})

    def test_info(self):
        res = self.client.get(u'/user/register', {'phone':'13345678907', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'13345678907', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'phone':'13345678907','exp':0,'level':u'青铜','score':0,'token':s_token,'avatar':'','uid':s_uid,'username':'13345678907','is_active':True, 'email':'', 'errno':0})

    def test_info_failed(self):
        res = self.client.get(u'/user/register', {'phone':'13345678908', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'13345678909', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg': 'username or password error'})

    def test_change_password(self):
        res = self.client.get(u'/user/register', {'phone':'13345678910', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/change_password', {'username':'13345678910', 'password':'abcdef', 'new_password':'133456'})
        s_token = json.loads(res.content)["token"]
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0,'username':'13345678910','token':s_token})
# login with old password
        res = self.client.get(u'/user/login', {'username':'13345678910','password':'abcdef'})
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})
        res = self.client.get(u'/user/login', {'username':'13345678910','password':'133456'})
        self.assertEqual(json.loads(res.content)["token"], s_token)

# same password but token changed
    def test_change_same_password(self):
        res = self.client.get(u'/user/register', {'phone':'13345678911', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/change_password', {'username':'13345678911', 'password':'abcdef', 'new_password':'abcdef'})
        s_token = json.loads(res.content)["token"]
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0,'username':'13345678911','token':s_token})
        res = self.client.get(u'/user/login', {'username':'13345678911','password':'abcdef'})
        self.assertEqual(json.loads(res.content)["token"], s_token)

    """
    def test_update_phone(self):
        res = self.client.get(u'/user/register', {'phone':'13345678912', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'13345678912', 'token':s_token, })
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0})
        mo_user = User.objects.get(name='13345678912')
        self.assertEqual(mo_user.phone, '10987654321')

    """
    def test_login_wrong_pass(self):
        self.client.get(u'/user/register',{'phone':'13345678913','password':'abcdef',})
        res = self.client.get(u'/user/login',{'username':'13345678913','password':'133456'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})

    def test_update_nothing(self):
        res = self.client.get(u'/user/register', {'phone':'13345678914', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        se_old_user = UserSerializer(User.objects.get(name='13345678914'))
        res = self.client.get(u'/user/update', {'username':'13345678914', 'token':s_token})
        se_new_user = UserSerializer(User.objects.get(name='13345678914'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(se_old_user.data, se_new_user.data)

    def test_feedback(self):
        s_content = u'hello world 中文测试'
        res = self.client.get(u'/user/register', {'phone':'13345678915', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/feedback', {'username':'13345678915', 'token':s_token, 'content':s_content})
        i_fid = json.loads(res.content)["fid"]
        self.assertJSONEqual(res.content, {'errno':0, 'fid':i_fid})
        mo_fb = Feedback.objects.get(fid=i_fid)
        self.assertEqual(mo_fb.content, s_content)

    def test_third_login(self):
        res = self.client.get(u'/user/third_login', {'third_tag':'qq', 'third_uid':'1234567','third_name':'abcdefg',})
        self.assertEqual(res.status_code, 200)
        #print res
        s_uid = json.loads(res.content)["uid"]
        s_username = json.loads(res.content)["username"]
        s_third_token = json.loads(res.content)["third_token"]
        res = self.client.get(u'/user/info', {'username':s_username, 'token':s_third_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'phone':'','exp':0,'level':u'青铜','score':0,'token':s_third_token,'avatar':'','uid':s_uid,'username':'abcdefg','is_active':True, 'email':'', 'errno':0})

    def test_third_bind(self):
        res = self.client.get(u'/user/register', {'phone':'13345678916', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/third_bind', {'username':'13345678916','token':s_token,'third_tag':'qq', 'third_uid':'1234568',})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678916')
        s_third_token = json.loads(res.content)["third_token"]
        self.assertEqual(mo_user.third_token, s_third_token)

    def test_third_bind_multi(self):
        res = self.client.get(u'/user/register', {'phone':'13345678917', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]

        res = self.client.get(u'/user/third_bind', {'username':'13345678917','token':s_token,'third_tag':'qq', 'third_uid':'1234569',})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678917')
        s_third_token = json.loads(res.content)["third_token"]
        self.assertEqual(mo_user.third_token, s_third_token)

        res = self.client.get(u'/user/third_bind', {'username':'13345678917','token':s_token,'third_tag':'wb', 'third_uid':'zyxwvu0',})
        self.assertEqual(res.status_code, 200)
        s_third_token = json.loads(res.content)["third_token"]
        mo_user = User.objects.get(name='13345678917')
        self.assertEqual(mo_user.third_token, s_third_token)
        self.assertEqual(mo_user.third_uids, 'qq$1234569|wb$zyxwvu0|')

    def test_third_bind_binded_same(self):
        res = self.client.get(u'/user/register', {'phone':'13345678918', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/third_bind', {'username':'13345678918','token':s_token,'third_tag':'qq', 'third_uid':'12345610',})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678918')
        s_third_token = json.loads(res.content)["third_token"]
        self.assertEqual(mo_user.third_token, s_third_token)
        res = self.client.get(u'/user/third_bind', {'username':'13345678918','token':s_token,'third_tag':'qq', 'third_uid':'12345610',})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno':0, 'third_token':s_third_token})

    def test_third_bind_binded_other(self):
        res = self.client.get(u'/user/register', {'phone':'13345678919', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/third_bind', {'username':'13345678919','token':s_token,'third_tag':'qq', 'third_uid':'12345611',})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678919')
        s_third_token = json.loads(res.content)["third_token"]
        self.assertEqual(mo_user.third_token, s_third_token)
        res = self.client.get(u'/user/register', {'phone':'13345678920', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/third_bind', {'username':'13345678920','token':s_token,'third_tag':'qq', 'third_uid':'12345611',})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':'this account has been binded'})

    def test_third_login_twice(self):
        res = self.client.get(u'/user/third_login', {'third_tag':'qq', 'third_uid':'12345612','third_name':'abcdef1'})
        self.assertEqual(res.status_code, 200)
        s_username = json.loads(res.content)["username"]
        s_third_token = json.loads(res.content)["third_token"]
        mo_user = User.objects.get(name=s_username)
        self.assertEqual(mo_user.third_token, s_third_token)

        res = self.client.get(u'/user/third_login', {'third_tag':'qq', 'third_uid':'12345612','third_name':'abcdef1'})
        self.assertEqual(res.status_code, 200)
        s_username = json.loads(res.content)["username"]
        s_third_token = json.loads(res.content)["third_token"]
        mo_user = User.objects.get(name=s_username)
        self.assertEqual(mo_user.third_token, s_third_token)

    def test_third_login_multi(self):
        res = self.client.get(u'/user/third_login', {'third_tag':'qq', 'third_uid':'12345613','third_name':'abcdef2'})
        self.assertEqual(res.status_code, 200)
        s_username = json.loads(res.content)["username"]
        s_third_token = json.loads(res.content)["third_token"]
        mo_user = User.objects.get(name=s_username)
        self.assertEqual(mo_user.third_token, s_third_token)

        res = self.client.get(u'/user/third_login', {'third_tag':'wb', 'third_uid':'12345613','third_name':'zyxwvu2'})
        self.assertEqual(res.status_code, 200)
        s_username = json.loads(res.content)["username"]
        s_third_token = json.loads(res.content)["third_token"]
        mo_user = User.objects.get(name=s_username)
        self.assertEqual(mo_user.third_token, s_third_token)

    def test_third_login_binded(self):
        res = self.client.get(u'/user/register', {'phone':'13345678921', 'password':'abcdef', })
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/third_bind', {'username':'13345678921','token':s_token,'third_tag':'qq', 'third_uid':'12345614',})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='13345678921')
        s_third_token = json.loads(res.content)["third_token"]
        self.assertEqual(mo_user.third_token, s_third_token)

        res = self.client.get(u'/user/third_login', {'third_tag':'qq', 'third_uid':'12345614','third_name':'abcdef3'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':'this account has been binded'})

