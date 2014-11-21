# coding=utf-8
from django.db import models
from WCLib.models import *
from WCLib.views import *
from WCCloth.models import Cloth
import ConfigParser
import OpenSSL.crypto as ct
import sys, json, base64, hashlib, httplib
import xml.etree.ElementTree as ET
from django.template import loader, Context
import datetime as dt
import uuid

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

    @classmethod
    def ImportOrders(cls, mo_shop, mo_bill):
        s_method_name = sys._getframe().f_code.co_name
        config = ConfigParser.ConfigParser()
        with open('rfd.conf', 'r') as rfdconf:
            config.readfp(rfdconf)
            s_url = config.get('common', 'url')
            s_port = config.get('common', 'port')
            s_company = config.get('common', 'company')
            s_default_zipcode = config.get('common', 'default_zipcode')
            s_merchant_code = config.get(s_method_name, 'merchant_code')
            s_template_file = config.get(s_method_name, 'template_file')
            s_order_template_file = config.get(s_method_name, 'order_template_file')

        d_import_orders = {
            "company": s_company,
            "dt": dt.datetime.now().strftime("%Y%m%d%H%M%S"),
            "once_key": uuid.uuid4(),
            "merchant_code": s_merchant_code,
            "bid": mo_bill.bid,
            "shop_name": mo_shop.name,
            "shop_province": mo_shop.province,
            "shop_city": mo_shop.city,
            "shop_area": mo_shop.area,
            "shop_address": mo_shop.address,
            "shop_phone": mo_shop.phone,
            "bill_total": mo_bill.total,
            "bill_paid": mo_bill.paid,
            "bill_receive": max(0, mo_bill.total - mo_bill.paid),
            "user_name": mo_bill.real_name,
            "user_province": mo_bill.province,
            "user_city": mo_bill.city,
            "user_area": mo_bill.area,
            "user_address": mo_bill.address,
            "user_phone": mo_bill.phone,
            "order_details": "",
        }
        js_cloth = mo_bill.clothes
        for it_cloth in js_cloth:
            try:
                i_cid = it_cloth.get('cid')
                i_num = it_cloth.get('number')
                mo_cloth = Cloth.objects.get(cid=i_cid,is_leaf=True)
                f_price = mo_cloth.price
                if not eq_zero(f_price):
                    t_order = loader.get_template(s_order_template_file)
                    d_order_detail = {
                        "cloth_name": mo_cloth.name,
                        "cloth_num": i_num,
                        "cloth_price": mo_cloth.price,
                        "cid": mo_cloth.cid,
                    }
                    c_order = Context(d_order_detail)
                    d_import_orders['order_details'] += t_order.render(c_order)
            except (AttributeError, Cloth.DoesNotExist) as e:
                continue

        t_response = loader.get_template(s_template_file)
        c_response = Context(d_import_orders)
        return t_response.render(c_response)

    def AddFetchOrder(self, mo_address, mo_bill):
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
        s_method_name = sys._getframe().f_code.co_name
        config = ConfigParser.ConfigParser()
        with open('rfd.conf', 'r') as rfdconf:
            config.readfp(rfdconf)
            s_lcid = config.get(s_method_name, 'lcid')
            s_xmlns = config.get(s_method_name, 'xmlns')
            s_pk_file = config.get(s_method_name, 'private_key')
            s_url = config.get('common', 'url')
            s_port = config.get('common', 'port')
            s_company = config.get('common', 'company')
            s_default_zipcode = config.get('common', 'default_zipcode')

        d_fetch_order = {
            "SendBy": mo_address.real_name,
            "MobilePhone": mo_address.phone,
            "Telephone": mo_address.phone,
            "PostCode": s_default_zipcode,
            "Company": s_company,
            "SendProvinceName": mo_address.province,
            "SendCityName": mo_address.city,
            "SendAreaName": mo_address.area,
            "SendAddress": mo_address.address,
            "NeedAmount": mo_bill.total,
            "ProtectPrice": 0
        }
        s_fetch_order = self.__class__.sign_data(d_fetch_order, s_pk_file)

        soap_msg = SM_TEMPLATE %{'method_name':s_method_name,
                                 's_fetch_order':s_fetch_order,
                                 's_lcid':s_lcid
                                }

        webservice = httplib.HTTP(s_url, i_port)
        webservice.putrequest("POST", "/DeliveryService.svc?wsdl")
        webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        webservice.putheader("Content-length", "%d" % len(soap_msg))
        s_soap_action = "\"http://tempuri.org/IDeliveryService/%s\"" %(s_method_name)
        webservice.putheader("SOAPAction", s_soap_action)
        webservice.endheaders()
        webservice.send(soap_msg)

        statuscode, statusmessage, header = webservice.getreply()
        s_xmlres = webservice.getfile().read()
        xml_res = ET.fromstring(s_xmlres)
        no_res = xml_res.find('.//{%s}AddFetchOrderResult' %(s_xmlns))
        if None == no_res:
            d_res = {'IsSucceed':false}
            return d_res
        d_res = json.loads(s_res)
        return d_res

    @classmethod
    def sign_data(cls, js_data, s_pk_file):
        if None == js_data:
            return None
        s_json = json.dumps(js_data, separators=(',', ':'))
        s_hash = base64.b64encode(hashlib.md5(s_json).digest())
        pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open(s_pk_file).read())
        s_res = s_json + ',' + base64.b64encode(ct.sign(pk_prikey, s_hash, 'sha1'))
        return s_res

class Address(models.Model):
    aid = models.AutoField(primary_key=True)
    own = models.ForeignKey('WCUser.User')
    real_name = models.CharField(max_length=255,default='')
    phone = models.CharField(max_length=12,default='')
    province = models.CharField(max_length=15,default='',choices=Province_Choice)
    city = models.CharField(max_length=63,default='',choices=City_Choice)
    area = models.CharField(max_length=15,default='',choices=Area_Choice)
    address = models.CharField(max_length=255,default='')
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "%d(%s)" % (self.aid, self.real_name)

    def get_full_address(self):
        if 0 == len(self.province + self.city + self.area):
            s_separator = ''
        else:
            s_separator = ' '
        return self.province + self.city + self.area + s_separator + self.address

    @classmethod
    def create(cls, mo_user, d_data):
        return cls(aid=None,own=mo_user, real_name=d_data.get('real_name'), \
                            province=d_data.get('province'),city=d_data.get('city'), \
                            area=d_data.get('area'), address=d_data.get('address'), \
                            phone=d_data.get('phone') )

    @classmethod
    def get_adr(cls, own_id, aid, deleted=False):
        try:
            mo_adr = cls.objects.get(own_id=own_id, aid=aid, deleted=deleted)
        except (cls.DoesNotExist) as e:
            return None
        return mo_adr
