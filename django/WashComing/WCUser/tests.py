# coding=utf-8
from django.test import TestCase, Client

# Create your tests here.
class UserTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register(self):
        res = self.client.get(u'/user/register?username=unittest&password=abcdef&phone=12345678901&invited_username=中文多少够')
        self.assertEqual(res.status_code, 200)
