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
    WASHING = 30 # nouse
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

    lid = models.AutoField(primary_key=True, verbose_name=u'如风达信息编号')
    status = models.IntegerField(default=0, verbose_name=u'信息状态')
    get_order_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'取衣受理单号', help_text=u'')
    get_way_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'取衣运单号', help_text=u'')
    get_form_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'取衣我方单号', help_text=u'这里实际和取衣订单号一致')
    get_message = models.CharField(max_length=255,default='',blank=True, \
        verbose_name=u'取衣最近一次信息', help_text=u'')
    get_operate_time = models.DateTimeField(default=dt.datetime(2014,1,1),blank=True, \
        verbose_name=u'取衣最近一次更新时间', help_text=u'')
    return_order_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'送衣受理单号', help_text=u'')
    return_way_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'送衣运单号', help_text=u'')
    return_form_no = models.CharField(max_length=31,default='',blank=True, \
        verbose_name=u'送衣我方单号', help_text=u'这里和运单号一致，如果需要手动更新，则修改这个号')
    return_message = models.CharField(max_length=255,default='',blank=True, \
        verbose_name=u'送衣最近一次信息', help_text=u'')
    return_operate_time = models.DateTimeField(default=dt.datetime(2014,1,1),blank=True, \
        verbose_name=u'送衣最近一次更新时间', help_text=u'')
    ext = JSONField(default=[],blank=True, verbose_name=u'扩展字段', \
        help_text=u'里面包含每次如风达更新状态信息')

# in parent directory
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    config = ConfigParser.ConfigParser()

    def __unicode__(self):
        if hasattr(self, 'bill_of'):
            return "%d bill[%s, %s] get[%s, %s] return[%s, %s]" %(self.lid, self.bill_of.bid, self.bill_of.real_name, self.get_way_no, self.get_order_no, self.return_way_no, self.return_order_no)
        return "%d" %(self.lid)

    @classmethod
    # return rfd response convert dict
    # to_shop is True then send custom to wash shop order(getting clothes)
    # to_shop is False then returnning clothes
    def ImportOrders(cls, mo_bill, to_shop=False):
        mo_shop = mo_bill.shop
        print mo_shop
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
        if to_shop: # (getting order)
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
# get cloth order DOES NOT pay
                "bill_total": 0,
                "bill_paid": 0,
                "bill_receive": 0,
                "shop_name": mo_bill.real_name,
                "shop_province": mo_bill.province,
                "shop_city": mo_bill.city,
                "shop_area": mo_bill.area,
                "shop_address": mo_bill.address,
                "shop_phone": mo_bill.phone,
                "comment": "%s至%s取 洗来了单号 %d" %(s_return_start, s_return_end, mo_bill.bid),
                "order_details": "",
            }
        else: # to_shop == False (returnning order)
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
                "comment": "%s至%s送到客户 洗来了单号 %d" %(s_return_start, s_return_end, mo_bill.bid),
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

        d_import_orders['shop_address'] = u"【洗来了 id:%d 共%d件】" \
            %(mo_bill.bid, i_clothes_number) + d_import_orders['shop_address']
        d_import_orders['user_address'] = u"【洗来了 id:%d 共%d件】" \
            %(mo_bill.bid, i_clothes_number) + d_import_orders['user_address']

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
    # to_shop is True then send custom to wash shop order(getting clothes)
    # to_shop is False then returnning clothes
    def AddFetchOrder(cls, mo_bill, to_shop=True):
        mo_shop = mo_bill.shop
        if not to_shop and None == mo_shop:
            d_res = {'IsSucceed':False, 'Message':'no shop info', 'Exception':''}
            return d_res
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
        if to_shop:
            s_dt_start = mo_bill.get_time_0.strftime(DATETIME_FORMAT_SHORT)
            s_dt_end = mo_bill.get_time_1.strftime(DATETIME_FORMAT_SHORT)
        else:
            s_dt_start = mo_bill.return_time_0.strftime(DATETIME_FORMAT_SHORT)
            s_dt_end = mo_bill.return_time_1.strftime(DATETIME_FORMAT_SHORT)
        f_total = float(mo_bill.total - mo_bill.paid)
        if to_shop:
            s_remark = u"%s至%s取" %(s_dt_start, s_dt_end)
        else:
            s_remark = u"应收%.2f元 POS机\n" %(f_total)
            s_remark += u"%s" %(mo_bill.address)
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
            s_clothes = u" 订单品类过多，请联系客服010-63132300获取详细信息"
        if to_shop:
            s_remark += s_clothes
        if len(s_remark.encode('utf-8')) > 100:
            s_remark = u"备注信息过长，收款及客户地址请联系客服010-63132300获取详细信息"
        if to_shop: # (getting order) sender is custom
            d_fetch_order = {
                "SendBy": mo_bill.real_name,
                "MobilePhone": mo_bill.phone,
                "Telephone": mo_bill.phone,
                "PostCode": s_default_zipcode,
                "Company": s_company,
                "SendProvinceName": mo_bill.province,
                "SendCityName": mo_bill.city,
                "SendAreaName": mo_bill.area,
                "SendAddress": u"【洗来了id:%d 共%d件】" %(mo_bill.bid, i_clothes_number) + mo_bill.address,
# get order may not get paid
                "NeedAmount": f_total,
                "ProtectPrice": 0,
                "Remark": s_remark,
            }
        else: # to_shop == False (returnning order) sender is wash shop
            d_fetch_order = {
                "SendBy": mo_shop.name,
                "MobilePhone": mo_shop.phone,
                "Telephone": mo_shop.phone,
                "PostCode": s_default_zipcode,
                "Company": s_company,
                "SendProvinceName": mo_shop.province,
                "SendCityName": mo_shop.city,
                "SendAreaName": mo_shop.area,
                "SendAddress": u"【洗来了id:%d 共%d件】" %(mo_bill.bid, i_clothes_number) + mo_shop.address,
                "NeedAmount": f_total,
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
        logging.debug(s_xmlres)
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
# i_type 1 for get order, 2 for get form, 3 for return form, 4 for return order, 9 for error
        try:
            if s_custom_order.startswith('SL'):
                i_type = 9
                q_rfd = cls.objects.filter(
                    Q(get_order_no=s_custom_order) | Q(return_order_no=s_custom_order)
                )
                if 0 == len(q_rfd):
                    d_ret['Ret'] = 1
                    d_ret['Message'] = 'array is empty op_id[%s] custom_order[%s]' \
                            %(s_operate_id, s_custom_order)
                    return d_ret
                elif len(q_rfd) > 1:
                    d_ret['Ret'] = 1
                    d_ret['Message'] = 'array is large thon 1 op_id[%s] custom_order[%s]' \
                            %(s_operate_id, s_custom_order)
                    return d_ret
                mo_rfd = q_rfd[0]
                if mo_rfd.get_order_no == s_custom_order:
                    i_type = 1
                elif mo_rfd.return_order_no == s_custom_order:
                    i_type = 4
                else:
                    logging.error('this is no science op_id[%s] custom_order[%s]' \
                                  %(s_operate_id, s_custom_order))
                    raise cls.DoesNotExist()
            else:
                i_type = 9
                q_rfd = cls.objects.filter(
                    Q(get_form_no=s_custom_order) | Q(return_form_no=s_custom_order)
                )
                if 0 == len(q_rfd):
                    d_ret['Ret'] = 1
                    d_ret['Message'] = 'array is empty op_id[%s] custom_order[%s]' \
                            %(s_operate_id, s_custom_order)
                    return d_ret
                elif len(q_rfd) > 1:
                    d_ret['Ret'] = 1
                    d_ret['Message'] = 'array is large thon 1 op_id[%s] custom_order[%s]' \
                            %(s_operate_id, s_custom_order)
                    return d_ret
                mo_rfd = q_rfd[0]
                if mo_rfd.get_form_no == s_custom_order:
                    i_type = 2
                elif mo_rfd.return_form_no == s_custom_order:
                    i_type = 3
                else:
                    logging.error('this is no science op_id[%s] custom_order[%s]' \
                                  %(s_operate_id, s_custom_order))
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
                    mo_bill.change_status(mo_bill.__class__.GETTING)
                if cls.SUCCESS == i_status:
                    mo_rfd.status = cls.GOT
                    mo_bill.change_status(mo_bill.__class__.WASHING)
            elif i_type in [3,4]:
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
                    mo_bill.change_status(mo_bill.__class__.RETURNNING)
                if cls.SUCCESS == i_status:
                    mo_rfd.status = cls.CLIENT_SIGN
                    mo_bill.change_status(mo_bill.__class__.NEED_FEEDBACK)
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
    aid = models.AutoField(primary_key=True, verbose_name=u'地址id', help_text=u'')
    own = models.ForeignKey('WCUser.User', verbose_name=u'用户id', help_text=u'')
    real_name = models.CharField(max_length=255,default='', verbose_name=u'姓名', help_text=u'')
    phone = models.CharField(max_length=12,default='', verbose_name=u'手机', help_text=u'')
    province = models.CharField(max_length=15,default='',choices=Province_Choice, \
        verbose_name=u'省', help_text=u'')
    city = models.CharField(max_length=63,default='',choices=City_Choice, \
        verbose_name=u'市', help_text=u'')
    area = models.CharField(max_length=15,default='',choices=Area_Choice, \
        verbose_name=u'区', help_text=u'')
    address = models.CharField(max_length=255,default='', verbose_name=u'地址', \
        help_text=u'')
    deleted = models.BooleanField(default=False, verbose_name=u'删除标志', help_text=u'')

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
        (ERROR, 'error'),
        (TODO, 'todo'),
        (DOING, 'doing'),
# add some other here
        (NO_DO_BUT_DONE, 'no_do_but_done'),
        (DONE, 'done'),
    )
    Nothing = 0
    AddFetchOrder = 1
    ImportOrders = 2
    GetOrderLog = 3
    ImportGettingOrders = 4
    AddReturnningFetchOrder = 5
    Type_Choice = (
        (Nothing, 'Nothing'),
        (AddFetchOrder, 'AddFetchOrder'),
        (ImportOrders, 'ImportOrders'),
        (GetOrderLog, 'GetOrderLog'),
        (ImportGettingOrders, 'ImportGettingOrders'),
        (AddReturnningFetchOrder, 'AddReturnningFetchOrder'),
    )

    qid = models.AutoField(primary_key=True, verbose_name=u'发单队列id', help_text=u'')
    bill = models.ForeignKey('WCBill.Bill',default=None,blank=True, verbose_name=u'关联订单', help_text=u'')
    type = models.IntegerField(default=0,choices=Type_Choice, verbose_name=u'发单类型', \
        help_text=u'取衣发受理单，取衣发订单（立即下单），送衣发订单')
    message = models.CharField(max_length=8195, verbose_name=u'错误信息', help_text=u'')
    status = models.IntegerField(default=0,choices=Status_Choice, \
        verbose_name=u'状态', help_text=u'')
    time = models.DateTimeField(db_index=True, verbose_name=u'触发时间', \
        help_text=u'系统时间大于这个时间则开始发单')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'更新时间', \
        help_text=u'最近一次尝试发单时间')

