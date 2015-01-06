from django.test import TestCase
from WCUser.models import User
from WCLogistics.models import Address
import datetime as dt

# Create your tests here.
class AddressTest(TestCase):
    def test_create(self):
        mo_user = User.objects.create(name='test')
        mo_adr = Address.objects.create(own_id=1)
