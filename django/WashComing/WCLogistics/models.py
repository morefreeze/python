# coding=utf-8
from django.db import models
from django.db.models import Q
from WCLib.models import *
from WCLib.views import *
from WCLib.serializers import *
from WCCloth.models import Cloth
import ConfigParser
import OpenSSL.crypto as ct
import sys, json, base64, hashlib, httplib
import xml.etree.ElementTree as ET
from django.template import loader, Context
import datetime as dt
import uuid
import urllib
import urllib2

# Create your models here.
class RFD(models.Model):
    GET_ABORT = -10
    RETURN_ABORT = -20
    ERROR = -100
    TO_GET = 5
    GETTING = 10
    GOT = 20
    WASHING = 30
    TO_RETURN = 40
    RETURNNING = 50
    CLIENT_SIGN = 100

# RFD order status
    ASSIGNED_SITE = -4
    IN_WAREHOUSE = 1
    DELIVERY = 2
    SUCCESS = 3
    STAY = 4
    REFUSAL = 5
    OUT_WAREHOUSE = 10

    lid = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)
    get_order_no = models.CharField(max_length=31,unique=True,default='',blank=True)
    get_way_no = models.CharField(max_length=31,default='',blank=True)
    get_form_no = models.CharField(max_length=31,default='',blank=True)
    get_message = models.CharField(max_length=255,default='',blank=True)
    get_operate_time = models.DateTimeField(default=dt.datetime(2000,1,1),blank=True)
    return_way_no = models.CharField(max_length=31,default='',blank=True)
    return_form_no = models.CharField(max_length=31,default='',blank=True)
    return_message = models.CharField(max_length=255,default='',blank=True)
    return_operate_time = models.DateTimeField(default=dt.datetime(2000,1,1),blank=True)
    ext = JSONField(default=[],blank=True)

# in parent directory
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    config = ConfigParser.ConfigParser()

    def __unicode__(self):
        return "%d get[%s] return[%s]" %(self.lid, self.get_way_no, self.return_way_no)

    @classmethod
    # return rfd response convert dict
    # reversed is True then send custom to wash shop order(getting clothes)
    # reversed is False then returnning clothes
    def ImportOrders(cls, mo_bill, reversed=False):
        mo_shop = mo_bill.shop
        if None == mo_shop:
            return {'ResultCode':'ImportFailure', 'ResultMessage':'no shop info'}
        s_method_name = sys._getframe().f_code.co_name
        with open(os.path.join(cls.conf_dir, 'rfd.conf'), 'r') as rfdconf:
            cls.config.readfp(rfdconf)
            s_url = cls.config.get('common', 'url')
            s_port = cls.config.get('common', 'port')
            s_company = cls.config.get('common', 'company')
            s_default_zipcode = cls.config.get('common', 'default_zipcode')
            s_merchant_code = cls.config.get('common', 'merchant_code')
            s_template_file = cls.config.get(s_method_name, 'template_file')
            s_order_template_file = cls.config.get(s_method_name, 'order_template_file')

        s_url = "http://%s:%s/api/" %(s_url, s_port)
        s_return_start = mo_bill.return_time_0.strftime(DATETIME_FORMAT_SHORT)
        s_return_end = mo_bill.return_time_1.strftime(DATETIME_FORMAT_SHORT)
        if reversed: # (getting order)
            d_import_orders = {
                "company": s_company,
                "dt": dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                "once_key": uuid.uuid4(),
                "merchant_code": s_merchant_code,
                "bid": mo_bill.bid,
                "user_name": mo_shop.name,
                "user_province": mo_shop.province,
                "user_city": mo_shop.city,
                "user_area": mo_shop.area,
                "user_address": mo_shop.address,
                "user_phone": mo_shop.phone,
                "bill_total": mo_bill.total,
                "bill_paid": mo_bill.paid,
                "bill_receive": max(0, mo_bill.total - mo_bill.paid),
                "shop_name": mo_bill.real_name,
                "shop_province": mo_bill.province,
                "shop_city": mo_bill.city,
                "shop_area": mo_bill.area,
                "shop_address": mo_bill.address,
                "shop_phone": mo_bill.phone,
                "comment": "%s至%s送" %(s_return_start, s_return_end),
                "order_details": "",
            }
        else: # reversed == False (returnning order)
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
                "comment": "%s至%s送" %(s_return_start, s_return_end),
                "order_details": "",
            }
        js_cloth = mo_bill.clothes
        i_clothes_number = 0
        for it_cloth in js_cloth:
            try:
                i_cid = it_cloth.get('cid')
                i_num = int(it_cloth.get('number'))
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
                    i_clothes_number += i_num
            except (AttributeError, Cloth.DoesNotExist) as e:
                continue

        d_import_orders['shop_address'] += u"[洗来了 id:%d 共%d件]" %(mo_bill.bid, i_clothes_number)
        d_import_orders['user_address'] += u"[洗来了 id:%d 共%d件]" %(mo_bill.bid, i_clothes_number)

        t_response = loader.get_template(s_template_file)
        c_response = Context(d_import_orders)
        s_xml = t_response.render(c_response).encode('utf-8')
        s_req_xml = cls.send_api(s_url, s_xml)
        d_res = {}
        try:
            logging.debug(s_req_xml)
            xml_req = ET.fromstring(s_req_xml)
            no_xml = xml_req.find('.//ImportResultDetail')
            for no_child in no_xml:
                d_res[no_child.tag] = no_child.text
        except Exception as e:
            # this follow rfd format
            d_res['ResultCode'] = 'ImportFailure'
            d_res['ResultMessage'] = e.__str__()
            return d_res
        return d_res

    @classmethod
    # return rfd response json
    def AddFetchOrder(cls, mo_bill):
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
        with open(os.path.join(cls.conf_dir, 'rfd.conf'), 'r') as rfdconf:
            cls.config.readfp(rfdconf)
            s_lcid = cls.config.get(s_method_name, 'lcid')
            s_xmlns = cls.config.get(s_method_name, 'xmlns')
            s_pk_file = os.path.join(cls.conf_dir, cls.config.get('common', 'private_key'))
            s_url = cls.config.get('common', 'url')
            s_port = cls.config.get('common', 'port')
            s_company = cls.config.get('common', 'company')
            s_default_zipcode = cls.config.get('common', 'default_zipcode')

        js_clothes = mo_bill.format_cloth()
        s_dt_start = mo_bill.get_time_0.strftime(DATETIME_FORMAT_SHORT)
        s_dt_end = mo_bill.get_time_1.strftime(DATETIME_FORMAT_SHORT)
        f_total = float(mo_bill.total)
        s_remark = u"%s至%s取 应收%.2f元 POS机" %(s_dt_start, s_dt_end, f_total)
        if len(js_clothes) == 0:
            d_res = {'IsSucceed':false, 'Message':'format clothes error', 'Exception':e.__str__()}
            return d_res
        s_clothes = ''
        i_clothes_number = 0
        for it_cloth in js_clothes:
            mo_cloth = Cloth.objects.get(cid=it_cloth['cid'])
# inquiry don't send to rfd
            if 'inquiry' in mo_cloth.ext and mo_cloth.ext['inquiry']:
                continue
            s_clothes += " %s %d" %(mo_cloth.get_name(), it_cloth['number'])
            i_clothes_number += int(it_cloth['number'])
# rfd remark len is 100
        if len(s_remark.encode('utf-8')) + len(s_clothes.encode('utf-8')) > 100:
            s_clothes = u" 订单品类过多，请联系客服获取详细信息 "
        s_remark += s_clothes
        d_fetch_order = {
            "SendBy": mo_bill.real_name,
            "MobilePhone": mo_bill.phone,
            "Telephone": mo_bill.phone,
            "PostCode": s_default_zipcode,
            "Company": s_company,
            "SendProvinceName": mo_bill.province,
            "SendCityName": mo_bill.city,
            "SendAreaName": mo_bill.area,
            "SendAddress": mo_bill.address + u"[洗来了 id:%d 共%d件]" %(mo_bill.bid, i_clothes_number),
            "NeedAmount": mo_bill.total,
            "ProtectPrice": 0,
            "Remark": s_remark,
        }
        s_fetch_order = cls.sign_data(d_fetch_order, s_pk_file)

        soap_msg = SM_TEMPLATE %{'method_name':s_method_name,
                                 's_fetch_order':s_fetch_order,
                                 's_lcid':s_lcid
                                }

        logging.debug(soap_msg)
        webservice = httplib.HTTP(s_url, s_port)
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
        try:
            no_res = xml_res.find('.//{%s}AddFetchOrderResult' %(s_xmlns))
            if None == no_res:
                d_res = {'IsSucceed':false}
        except e:
            d_res = {'IsSucceed':false, 'Message':'get xml result error', 'Exception':e.__str__()}
            return d_res
# {u'Message': u'SL141202000001', u'Exception': None, u'IsSucceed': True}
        d_res = json.loads(no_res.text)
        return d_res

    @classmethod
    # return render xml text in json
    # {'errno':0, 'xml':'...'}
    def PostStatus(cls, a_st):
        s_method_name = sys._getframe().f_code.co_name
        with open(os.path.join(cls.conf_dir, 'rfd.conf'), 'r') as rfdconf:
            cls.config.readfp(rfdconf)
            s_url = cls.config.get('common', 'url')
            s_port = cls.config.get('common', 'port')
            s_company = cls.config.get('common', 'company')
            s_template_file = cls.config.get(s_method_name, 'template_file')
            s_status_template_file = cls.config.get(s_method_name, 'status_template_file')

        d_post_status = {
            "company": s_company,
            "dt": dt.datetime.now().strftime("%Y%m%d%H%M%S"),
            "status_infos": "",
        }
        for it_st in a_st:
            if 0 == it_st.get('Ret'):
                is_success = 1
            else:
                is_success = 0
            d_st = {
                "op_id": it_st.get('OperateId'),
                "is_success": is_success,
                "message": it_st.get('Message'),
                "way_no": it_st.get('WaybillNo'),
            }
            t_status_info = loader.get_template(s_status_template_file)
            c_status_info = Context(d_st)
            d_post_status['status_infos'] += t_status_info.render(c_status_info)
        t_response = loader.get_template(s_template_file)
        c_response = Context(d_post_status)
        return {'errno':0, 'xml':t_response.render(c_response)}

    @classmethod
    def send_api(cls, s_url, s_xml):
        logging.debug(s_xml)
        with open(os.path.join(cls.conf_dir, 'rfd.conf'), 'r') as rfdconf:
            cls.config.readfp(rfdconf)
            s_company = cls.config.get('common', 'company')
            s_merchant_code = cls.config.get('common', 'merchant_code')
            s_pk_file = os.path.join(cls.conf_dir, cls.config.get('common', 'private_key'))
        pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open(s_pk_file).read())
        s_sign = base64.b64encode(ct.sign(pk_prikey, s_xml, 'sha1'))
        s_token = s_merchant_code + "|" + s_sign

        header = {'token':s_token, 'Content-Type':'text/xml; charset=utf-8'}
        req = urllib2.Request(s_url, s_xml, header)
        response = urllib2.urlopen(req)
        page = response.read()
        return page

    @classmethod
    # because function etree_to_dict convert dict like this:
    # [{'OperateId':{}, '_text':111}, {'WaybillNo':{}, '_text':123}]
    # so convert above to normal dict
    def get_status_info(cls, d_st):
        d_res = {}
        s_params = ['OperateId', 'WaybillNo', 'CustomerOrder', 'Result',
                   'Status', 'OperateTime', 'Operator',]
        for it_st in d_st:
            for s_param in s_params:
                if s_param in it_st:
                    d_res[s_param] = it_st['_text']
                    break
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

    @classmethod
    def update(cls, d_st_info):
        s_operate_id = d_st_info.get('OperateId')
        s_custom_order = d_st_info.get('CustomerOrder')
        s_waybill_no = d_st_info.get('WaybillNo')
        d_ret = {
            'Ret': 9,
            'Message': 'unknown error',
            'WaybillNo': s_waybill_no,
            'OperateId': s_operate_id,
        }
# i_type 1,2 for get form, 3 for return form, 4 for error
        try:
            if s_custom_order.startswith('SL'):
                i_type = 1
                mo_rfd = cls.objects.get(get_order_no=s_custom_order)
            else:
                i_type = 4
                q_rfd = cls.objects.filter(
                    Q(get_form_no=s_custom_order) | Q(return_form_no=s_custom_order)
                )
                if 0 == len(q_rfd):
                    d_ret['Ret'] = 1
                    d_ret['Message'] = 'array is empty op_id[%s] custom_order[%s]' \
                            %(s_operate_id, s_custom_order)
                    return d_ret
                mo_rfd = q_rfd[0]
                if mo_rfd.get_form_no == s_custom_order:
                    i_type = 2
                elif mo_rfd.return_form_no == s_custom_order:
                    i_type = 3
                else:
                    raise cls.DoesNotExist()
            i_status = int(d_st_info.get('Status'))
            s_message = d_st_info.get('Result')
            dt_operate_time = dt.datetime.strptime(d_st_info.get('OperateTime'),"%Y%m%d%H%M%S")
            mo_rfd.ext.append(d_st_info)
            mo_rfd.save()
            try:
                mo_bill = mo_rfd.bill_of
            except Exception as e:
                mo_rfd.ext['error'] = e.__str__()
                mo_rfd.save()
                d_ret['Ret'] = 3
                d_ret['Message'] = 'no bill bind this rfd order'
                return d_ret
            if i_type in [1, 2]:
                if dt_operate_time < mo_rfd.get_operate_time:
                    d_ret['Ret'] = 0
                    d_ret['Message'] = 'operate time passed(not error) time[%s]' %dt_operate_time
                    return d_ret
                mo_rfd.get_message = s_message
                mo_rfd.get_way_no = s_waybill_no
                mo_rfd.get_operate_time = dt_operate_time
                if i_status in [cls.ASSIGNED_SITE, cls.IN_WAREHOUSE,
                                cls.DELIVERY, cls.STAY, cls.OUT_WAREHOUSE]:
                    mo_rfd.status = cls.GETTING
                    mo_bill.status = mo_bill.__class__.GETTING
                    mo_bill.add_time(mo_bill.__class__.GETTING)
                if cls.SUCCESS == i_status:
                    mo_rfd.status = cls.GOT
                    mo_bill.status = mo_bill.__class__.WASHING
                    mo_bill.add_time(mo_bill.__class__.WASHING)
            elif 3 == i_type:
                if dt_operate_time < mo_rfd.return_operate_time:
                    d_ret['Ret'] = 0
                    d_ret['Message'] = 'operate time passed(not error) time[%s]' %dt_operate_time
                    return d_ret
                mo_rfd.return_message = s_message
                mo_rfd.return_way_no = s_waybill_no
                mo_rfd.return_operate_time = dt_operate_time
                if i_status in [cls.ASSIGNED_SITE, cls.IN_WAREHOUSE,
                                cls.DELIVERY, cls.STAY, cls.OUT_WAREHOUSE]:
                    mo_rfd.status = cls.RETURNNING
                    mo_bill.status = mo_bill.__class__.RETURNNING
                    mo_bill.add_time(mo_bill.__class__.RETURNNING)
                if cls.SUCCESS == i_status:
                    mo_rfd.status = cls.CLIENT_SIGN
                    mo_bill.status = mo_bill.__class__.NEED_FEEDBACK
                    mo_bill.add_time(mo_bill.__class__.NEED_FEEDBACK)
            mo_rfd.save()
            mo_bill.save()
        except (Exception) as e:
            logging.error("invalid rfd post status op_id[%s] custom[%s]" %(s_operate_id, s_custom_order))
            d_ret['Ret'] = 2
            d_ret['Message'] = e.__str__()
            return d_ret
        d_ret['Ret'] = 0
        d_ret['Message'] = ''
        return d_ret

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

# order queue for logistics
# some script fetch queue for sending order request to logistics
class OrderQueue(models.Model):
    ERROR = -1
    TODO = 0
    DOING = 10
    NO_DO_BUT_DONE = 90 # bill may be cancel
    DONE = 100
    Status_Choice = (
        (-1, 'error'),
        (0, 'todo'),
        (10, 'doing'),
# add some other here
        (90, 'no_do_but_done'),
        (100, 'done'),
    )
    Nothing = 0
    AddFetchOrder = 1
    ImportOrders = 2
    GetOrderLog = 3
    ImportGettingOrders = 4
    Type_Choice = (
        (Nothing, 'Nothing'),
        (AddFetchOrder, 'AddFetchOrder'),
        (ImportOrders, 'ImportOrders'),
        (GetOrderLog, 'GetOrderLog'),
        (ImportGettingOrders, 'ImportGettingOrders'),
    )

    qid = models.AutoField(primary_key=True)
    bill = models.ForeignKey('WCBill.Bill',default=None,blank=True)
    type = models.IntegerField(default=0,choices=Type_Choice)
    message = models.CharField(max_length=8195)
    status = models.IntegerField(default=0,choices=Status_Choice)
    time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(auto_now=True)

