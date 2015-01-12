# coding=utf-8
from django.views.decorators.http import require_http_methods
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
@require_http_methods(['POST', 'GET'])
def add(request):
    fo_adr = AddressAddForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def update(request):
    fo_adr = AddressUpdateForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def delete(request):
    fo_adr = AddressDeleteForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def list(request):
    fo_adr = AddressListForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def set_default(request):
    fo_adr = AddressSetDefaultForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def info(request):
    fo_adr = AddressInfoForm(dict(request.GET.items() + request.POST.items()))
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
@require_http_methods(['POST', 'GET'])
def list_lg(request):
    fo_adr = AddressXXXXXForm(dict(request.GET.items() + request.POST.items()))
    if not fo_adr.is_valid():
        return JSONResponse({'errmsg':fo_adr.errors})
    d_data = fo_adr.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    # todo

@require_http_methods(['POST', 'GET'])
def info_lg(request):
    fo_adr = AddressXXXXXForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def post_status(request):
    logging.debug(request.body)
    xml_res = ET.fromstring(request.body)
    d_xml = etree_to_dict(xml_res)
    if not 'Request' in d_xml:
        return HttpResponse("no Request")
    d_body = d_xml['Request'][1]['Body']
    a_st_info = []
# to sort operate time
    d_sort_time = {}
    for it_status_info in d_body:
        d_status_info = RFD.get_status_info(it_status_info['StatusInfo'])
        a_st_info.append(d_status_info)
        d_sort_time[ d_status_info['OperateId'] ] = d_status_info['OperateTime']
    l_sort_time = sorted(d_sort_time.items(), key=lambda e:e[1])
    a_res = []
    for s_OperateId, s_OperateTime in l_sort_time:
        for it_st_info in a_st_info:
            if it_st_info['OperateId'] == s_OperateId:
                d_ret = RFD.update(it_st_info)
                if d_ret['Ret'] != 0:
                    logging.error("post status error: %s" %(d_ret['Message']))
                a_res.append(d_ret)
    js_xml = RFD.PostStatus(a_res)
    logging.debug(js_xml['xml'])
    return HttpResponse(js_xml['xml'],content_type="application/xhtml+xml")

"""
@require_http_methods(['POST', 'GET'])
def submit(request):
    fo_adr = AddressXXXXXForm(dict(request.GET.items() + request.POST.items()))
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
