# coding=utf-8
from django.test import TestCase, Client
import json
from WCUser.models import User
from WCUser.serializers import UserSerializer

# Create your tests here.
class UserTest(TestCase):
    def test_register(self):
        res = self.client.get(u'/user/register', {'email':'unittest0@qq.com@qq.com', 'password':'abcdef','phone':'12345678901'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_dup(self):
        self.client.get(u'/user/register', {'email':'unittest1@qq.com','password':'abcdef','phone':'12345678901'})
        res = self.client.get(u'/user/register', {'email':'unittest1@qq.com','password':'abcdef','phone':'12345678901'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": "username has been registered"})

    def test_login(self):
        self.client.get(u'/user/register',{'email':'unittest2@qq.com','password':'abcdef','phone':'12345678901'})
        res = self.client.get(u'/user/login',{'username':'unittest2@qq.com','password':'abcdef'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_login_wrong_pass(self):
        self.client.get(u'/user/register',{'email':'unittest02@qq.com','password':'abcdef','phone':'12345678901'})
        res = self.client.get(u'/user/login',{'username':'unittest02@qq.com','password':'123456'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})

    def test_register_miss_field(self):
        res = self.client.get(u'/user/register',{'password':'abcdef','phone':'12345678901'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"email": ["This field is required."]}})

        res = self.client.get(u'/user/register',{'email':'unittest3@qq.com','phone':'12345678901'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"password": ["This field is required."]}})

        res = self.client.get(u'/user/register',{'email':'unittest3@qq.com','password':'abcdef'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"errmsg": {"phone": ["This field is required."]}})

        res = self.client.get(u'/user/register',{'email':'unittest3@qq.com','password':'abcdef','phone':'12345678901'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_register_invite(self):
        self.client.get(u'/user/register',{'email':'unittest4@qq.com','password':'abcdef','phone':'12345678901'})
        res = self.client.get(u'/user/register',{'email':'unittest5@qq.com','password':'abcdef','phone':'12345678901','invited_username':'unittest4@qq.com'})
        self.assertEqual(res.status_code, 200)
        mo_user = User.objects.get(name='unittest5@qq.com')
        mo_inv_user = mo_user.invited
        self.assertEqual(mo_inv_user.name, 'unittest4@qq.com')

    def test_register_invite_nouser(self):
        res = self.client.get(u'/user/register',{'email':'unittest6@qq.com','password':'abcdef','phone':'12345678901','invited_username':'NoThisUser'})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg':"invited user[NoThisUser] not found"})

    def test_info(self):
        res = self.client.get(u'/user/register', {'email':'unittest7@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'unittest7@qq.com', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'email':'unittest7@qq.com','exp':0,'level':42,'score':0,'token':s_token,'uid':s_uid,'username':'unittest7@qq.com','errno':0})

    def test_info_failed(self):
        res = self.client.get(u'/user/register', {'email':'unittest8@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        s_uid = json.loads(res.content)["uid"]
        res = self.client.get(u'/user/info', {'username':'unittest9@qq.com', 'token':s_token})
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errmsg': 'username or password error'})

    def test_update_password(self):
        res = self.client.get(u'/user/register', {'email':'unittest11@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest11@qq.com', 'token':s_token, 'password':'123456'})
        s_token = json.loads(res.content)["token"]
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest11@qq.com','token':s_token})
# login with old password
        res = self.client.get(u'/user/login', {'username':'unittest11@qq.com','password':'abcdef'})
        self.assertJSONEqual(res.content, {'errmsg':'username or password error'})
        res = self.client.get(u'/user/login', {'username':'unittest11@qq.com','password':'123456'})
        self.assertEqual(json.loads(res.content)["token"], s_token)

    def test_update_phone(self):
        res = self.client.get(u'/user/register', {'email':'unittest12@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest12@qq.com', 'token':s_token, 'phone':'10987654321'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest12@qq.com','token':s_token})
        mo_user = User.objects.get(name='unittest12@qq.com')
        self.assertEqual(mo_user.phone, '10987654321')

    def test_update_phone_password(self):
        res = self.client.get(u'/user/register', {'email':'unittest13@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        res = self.client.get(u'/user/update', {'username':'unittest13@qq.com', 'token':s_token, 'password':'123456', 'phone':'10987654321'})
        self.assertEqual(res.status_code, 200)
        s_token = json.loads(res.content)["token"]
        self.assertJSONEqual(res.content, {'errno': 0,'username':'unittest13@qq.com','token':s_token})
        mo_user = User.objects.get(name='unittest13@qq.com')
        self.assertEqual(mo_user.token, s_token)
        self.assertEqual(mo_user.phone, '10987654321')

    def test_update_nothing(self):
        res = self.client.get(u'/user/register', {'email':'unittest14@qq.com', 'password':'abcdef', 'phone':'12345678901'})
        s_token = json.loads(res.content)["token"]
        se_old_user = UserSerializer(User.objects.get(name='unittest14@qq.com'))
        res = self.client.get(u'/user/update', {'username':'unittest14@qq.com', 'token':s_token})
        se_new_user = UserSerializer(User.objects.get(name='unittest14@qq.com'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(se_old_user.data, se_new_user.data)

