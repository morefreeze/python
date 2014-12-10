# coding=utf-8
from WCLib.views import *
from WCLogistics.models import RFD, Address
from WCLogistics.forms import AddressAddForm, AddressUpdateForm, AddressDeleteForm, \
        AddressListForm, AddressSetDefaultForm, AddressInfoForm
from WCLogistics.serializers import AddressSerializer
from WCUser.models import User, Shop
from WCUser.serializers import UserSerializer
from WCBill.models import Bill
import OpenSSL.crypto as ct
import hashlib, base64
import json
# Create your views here.

#============Address method
def add(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressAddForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_adr = Address.create(mo_user, request.GET)
    mo_adr.save()
    b_set_default = d_data.get('set_default')
    if True == b_set_default:
        mo_user.default_adr = mo_adr
        mo_user.save()
    return JSONResponse({'errno':0, 'aid':mo_adr.aid})

def update(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressUpdateForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    i_aid = d_data.get('aid')
    mo_adr = Address.get_adr(mo_user.uid, i_aid)
    if None == mo_adr:
        return JSONResponse({'errmsg':'address not exist'})
    if None != d_data.get('real_name') and '' != d_data.get('real_name'):
        mo_adr.real_name = d_data.get('real_name')
    if None != d_data.get('province') and '' != d_data.get('province'):
        mo_adr.province = d_data.get('province')
    if None != d_data.get('city') and '' != d_data.get('city'):
        mo_adr.city = d_data.get('city')
    if None != d_data.get('area') and '' != d_data.get('area'):
        mo_adr.area = d_data.get('area')
    if None != d_data.get('address') and '' != d_data.get('address'):
        mo_adr.address = d_data.get('address')
    if None != d_data.get('phone') and '' != d_data.get('phone'):
        mo_adr.phone = d_data.get('phone')
    mo_adr.save()
    return JSONResponse({'errno':0})

def delete(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressDeleteForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    i_aid = d_data.get('aid')
    mo_adr = Address.get_adr(mo_user.uid, i_aid)
    if None == mo_adr:
        return JSONResponse({'errmsg':'address not exist'})
    mo_adr.deleted = True
    mo_adr.save()
    return JSONResponse({'errno':0})

def list(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressListForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    a_adr = Address.objects.filter(own=mo_user, deleted=False)
# get user's default address
    d_response = dict()
    d_response['data'] = []
    if None != a_adr:
        for it_adr in a_adr:
            se_adr = AddressSerializer(it_adr)
            if None != mo_user.default_adr and it_adr.aid == mo_user.default_adr.aid:
                se_adr.data['set_default'] = True
            d_response['data'].append(se_adr.data)
    d_response['count'] = len(d_response['data'])
    d_response['errno'] = 0
    return JSONResponse(d_response)

def set_default(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressSetDefaultForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    i_aid = d_data.get('aid')
    mo_adr = Address.get_adr(mo_user.uid, i_aid)
    if None == mo_adr:
        return JSONResponse({'errmsg':'address not exist'})
    mo_user.default_adr = mo_adr
    mo_user.save()
    return JSONResponse({'errno':0})

def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressInfoForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    i_aid = d_data.get('aid')
    mo_adr = Address.get_adr(mo_user.uid, i_aid)
    if None == mo_adr:
        return JSONResponse({'errmsg':'address not exist'})
    se_adr = AddressSerializer(mo_adr)
    d_response = dict()
    d_response = se_adr.data
    d_response['default'] = (mo_user.default_adr.aid == mo_adr.aid)
    d_response['errno'] = 0
    return JSONResponse(d_response)

#==============RFD method
def list_lg(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressXXXXXForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    # todo

def info_lg(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressXXXXXForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_adr = Address()
    # todo

def sign_data(js_data):
    if None == js_data:
        return None
    conf_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    s_hash = base64.b64encode(hashlib.md5(json.dumps(js_data)).digest())
    pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open(os.path.join(conf_dir,'rfd.pem')).read())
    s_res = s_json + ',' + base64.b64encode(ct.sign(pk_prikey, s_hash, 'sha1'))
    return s_res

def test_order(request):
    mo_bill = Bill.objects.get(bid=request.GET.get('bid'))
    tt = RFD()
    js_s = tt.AddFetchOrder(mo_bill)
    return JSONResponse(js_s)

def post_status(request):
    xml_res = ET.fromstring(request.body)
    d_xml = etree_to_dict(xml_res)
    if not 'Request' in d_xml:
        return HttpResponse("no Request")
    d_body = d_xml['Request'][1]['Body']
    a_st_info = []
    for it_status_info in d_body:
        d_status_info = RFD.get_status_info(it_status_info['StatusInfo'])
        a_st_info.append(d_status_info)
    a_res = []
    for it_st_info in a_st_info:
        d_ret = RFD.update(it_st_info)
        a_res.append(d_ret)
    js_xml = RFD.PostStatus(a_res)
    return HttpResponse(js_xml['xml'],content_type="application/xhtml+xml")

def test_import(request):
    mo_shop = Shop.objects.get(sid=1)
    mo_bill = Bill.objects.get(bid=2)
    mo_bill.format_cloth()
    mo_bill.save()
    s_s = ''
    """
    for it_cloth in mo_bill.clothes:
        mo_cloth = Cloth.objects.get(cid=it_cloth['cid'])
        s_s += " %s %d" %(mo_cloth.get_name(), it_cloth['number'])
    return HttpResponse(s_s)
    """
    d_res = RFD.ImportOrders(mo_bill)
    return JSONResponse(d_res)

"""
def submit(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_adr = AddressXXXXXForm(request.GET)
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_adr = Address()
"""
