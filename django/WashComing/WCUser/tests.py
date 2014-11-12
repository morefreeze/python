# coding=utf-8
from django.test import TestCase, Client
import json
from WCUser.models import User
from WCUser.serializers import UserSerializer

# Create your tests here.
class UserTest(TestCase):
    def test_register(self):
        res = self.client.get(u'/user/register?username=unittest0&password=abcdef&phone=12345678901')
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_dup(self):
        self.client.get(u'/user/register?username=unittest1&password=abcdef&phone=12345678901')
        res = self.client.get(u'/user/register?username=unittest1&password=abcdef&phone=12345678901')
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": "username has been registered"})

    def test_login(self):
        self.client.get(u'/user/register?username=unittest2&password=abcdef&phone=12345678901')
        res = self.client.get(u'/user/login?username=unittest2&password=abcdef')
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_login_wrong_pass(self):
        self.client.get(u'/user/register',{'username':'unittest02','password':'abcdef','phone':'12345678901'})
        res = self.client.get(u'/user/login',{'username':'unittest02','password':'123456'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})

    def test_register_miss_field(self):
        res = self.client.get(u'/user/register?password=abcdef&phone=12345678901')
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"username": ["This field is required."]}})

        res = self.client.get(u'/user/register?username=unittest3&phone=12345678901')
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"password": ["This field is required."]}})

        res = self.client.get(u'/user/register?username=unittest3&password=abcdef')
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"phone": ["This field is required."]}})

        res = self.client.get(u'/user/register?username=unittest3&password=abcdef&phone=12345678901')
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_invite(self):
        self.client.get(u'/user/register?username=unittest4&password=abcdef&phone=12345678901')
        res = self.client.get(u'/user/register?username=unittest5&password=abcdef&phone=12345678901&invited_username=unittest4')
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='unittest5')
        mo_inv_user = mo_user.invited
        self.assertEqual(mo_inv_user.name, 'unittest4')

    def test_register_invite_nouser(self):
        res = self.client.get(u'/user/register?username=unittest6&password=abcdef&phone=12345678901&invited_username=NoThisUser')
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':"invited user[NoThisUser] not found"})

    def test_info(self):
        res = self.client.get(u'/user/register', {'username':'unittest7', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'unittest7', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'email':'','exp':0,'level':42,'score':0,'token':s_token,'uid':s_uid,'username':'unittest7','errno':0})

    def test_info_failed(self):
        res = self.client.get(u'/user/register', {'username':'unittest8', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'unittest9', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg': 'username or password error'})

    def test_bind_email(self):
        res = self.client.get(u'/user/register', {'username':'unittest10', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/bind_email', {'username':'unittest10', 'token':s_token, 'email':'unittest10@wc.com'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0})
        mo_user = User.objects.get(name='unittest10')
        self.assertEqual(mo_user.email, 'unittest10@wc.com')

    def test_update_password(self):
        res = self.client.get(u'/user/register', {'username':'unittest11', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest11', 'token':s_token, 'password':'123456'})
        s_token = json.loads(res.content)["token"]
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest11','token':s_token})
# login with old password
        res = self.client.get(u'/user/login', {'username':'unittest11','password':'abcdef'})
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})
        res = self.client.get(u'/user/login', {'username':'unittest11','password':'123456'})
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_update_phone(self):
        res = self.client.get(u'/user/register', {'username':'unittest12', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest12', 'token':s_token, 'phone':'10987654321'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest12','token':s_token})
        mo_user = User.objects.get(name='unittest12')
        self.assertEqual(mo_user.phone, '10987654321')

    def test_update_phone_password(self):
        res = self.client.get(u'/user/register', {'username':'unittest13', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest13', 'token':s_token, 'password':'123456', 'phone':'10987654321'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest13','token':s_token})
        mo_user = User.objects.get(name='unittest13')
        self.assertEqual(mo_user.token, s_token)
        self.assertEqual(mo_user.phone, '10987654321')

    def test_update_nothing(self):
        res = self.client.get(u'/user/register', {'username':'unittest14', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        se_old_user = UserSerializer(User.objects.get(name='unittest14'))
        res = self.client.get(u'/user/update', {'username':'unittest14', 'token':s_token})
        se_new_user = UserSerializer(User.objects.get(name='unittest14'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(se_old_user.data, se_new_user.data)

