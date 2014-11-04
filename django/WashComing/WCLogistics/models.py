# coding=utf-8
from django.db import models
import ConfigParser
import OpenSSL.crypto as ct
import sys, json, base64, hashlib, httplib

# Create your models here.
class RFD(models.Model):
    lid = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)
    get_way_no = models.IntegerField(default=0)
    get_form_no = models.IntegerField(default=0)
    get_message = models.CharField(max_length=255,default='')
    return_way_no = models.IntegerField(default=0)
    return_form_no = models.IntegerField(default=0)
    return_message = models.CharField(max_length=255,default='')

    def ImportOrders(self):
        pass

    def AddFetchOrder(self, mo_address):
        SM_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:ns1="http://tempuri.org/">
<SOAP-ENV:Body>
<ns1:%(method_name)s>
<ns1:strFetchOrder>%(s_fetch_order)s</ns1:strFetchOrder>
<ns1:strLcid>%(s_lcid)s</ns1:strLcid>
</ns1:%(method_name)s>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'''
        d_fetch_order = {
            "SendBy": mo_address.real_name,
            "MobilePhone": mo_address.phone,
            "Telephone": mo_address.phone,
            "PostCode": "110000",
            "Company": "xll",
            "SendProvinceName": mo_address.provice,
            "SendCityName": mo_address.city,
            "SendAreaName": mo_address.area,
            "SendAddress": mo_address.address,
            "NeedAmount": "32.4",
            "ProtectPrice": 0
        }

        s_method_name = sys._getframe().f_code.co_name
        s_fetch_order = self.__class__.sign_data(d_fetch_order)
        config = ConfigParser.ConfigParser()
        with open('rfd.conf', 'r') as rfdconf:
            config.readfp(rfdconf)
            s_lcid = config.get(s_method_name, 'lcid')

        soap_msg = SM_TEMPLATE %{'method_name':s_method_name,
                                 's_fetch_order':s_fetch_order,
                                 's_lcid':s_lcid
                                }

        webservice = httplib.HTTP("61.51.37.70", 8082)
        webservice.putrequest("POST", "/DeliveryService.svc?wsdl")
        webservice.putheader("User-Agent", "Python post")
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(soap_msg))
        s_soap_action = "\"http://tempuri.org/IDeliveryService/%s\"" %(s_method_name)
        webservice.putheader("SOAPAction", s_soap_action)
        webservice.endheaders()
        webservice.send(soap_msg)

        statuscode, statusmessage, header = webservice.getreply()
        res = webservice.getfile().read()
        return res

    @classmethod
    def sign_data(cls, js_data):
        if None == js_data:
            return None
        s_json = json.dumps(js_data, separators=(',', ':'))
        s_hash = base64.b64encode(hashlib.md5(s_json).digest())
        pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open('rfd.pem').read())
        s_res = s_json + ',' + base64.b64encode(ct.sign(pk_prikey, s_hash, 'sha1'))
        return s_res


    def gen_get_bill(self, mo_user, mo_shop):
        [self.get_way_no, self.get_form_no] = rfd_ImportOrders()

class Address(models.Model):
    aid = models.AutoField(primary_key=True)
    own = models.ForeignKey('WCUser.User')
    real_name = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    provice = models.CharField(max_length=15,default='')
    city = models.CharField(max_length=63,default='')
    area = models.CharField(max_length=63,default='')
    address = models.CharField(max_length=255,default='')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%d(%s)" % (self.aid, self.real_name)

    @classmethod
    def create(cls, mo_user, d_data):
        return cls(aid=None,own=mo_user, real_name=d_data.get('real_name'), \
                               provice=d_data.get('provice'),city=d_data.get('city'), \
                            phone=d_data.get('phone'), address=d_data.get('address') )

    @classmethod
    def get_adr(cls, own_id, aid, deleted=False):
        try:
            mo_adr = cls.objects.get(own_id=own_id, aid=aid, deleted=deleted)
        except (cls.DoesNotExist) as e:
            return None
        return mo_adr
