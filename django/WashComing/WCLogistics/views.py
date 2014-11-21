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
    if '' != d_data.get('real_name'):
        mo_adr.real_name = d_data.get('real_name')
    if '' != d_data.get('province'):
        mo_adr.province = d_data.get('province')
    if '' != d_data.get('city'):
        mo_adr.city = d_data.get('city')
    if '' != d_data.get('area'):
        mo_adr.area = d_data.get('area')
    if '' != d_data.get('address'):
        mo_adr.address = d_data.get('address')
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

def test_sign(request):
    mo_address = Address.objects.get(aid=request.GET.get('aid'))
    mo_bill = Address.objects.get(bid=request.GET.get('bid'))
    tt = RFD()
    s_s = tt.AddFetchOrder(mo_address, mo_bill)
    #s_s = request.GET.get('s')
    return JSONResponse({'res':s_s})

def sign_data(js_data):
    if None == js_data:
        return None
    s_hash = base64.b64encode(hashlib.md5(json.dumps(js_data)).digest())
    pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open('rfd.pem').read())
    s_res = s_json + ',' + base64.b64encode(ct.sign(pk_prikey, s_hash, 'sha1'))
    return s_res

def test_post_status(request):
    POST_STATUS_TEMPLATE = """
    <Response>
        <Head>
            <Service>PostStatus</Service>
            <ServiceVersion>1.0</ServiceVersion>
            <SrcSys> rfd </SrcSys>
            <DstSys>demo</DstSys>
            <DateTime>20131127132426</DateTime>
        </Head>
        <Body>
            <StatusInfo>
                <OperateId>111</OperateId>
                <IsSuccess>0</IsSuccess>
                <Message>网络异常</Message>
                <WaybillNo>111</WaybillNo>
            </StatusInfo>
            <StatusInfo>
                <OperateId>222</OperateId>
                <IsSuccess>0</IsSuccess>
                <Message>网络异常</Message>
                <WaybillNo>222</WaybillNo>
            </StatusInfo>
        </Body>
    </Response>
    """
    return HttpResponse(POST_STATUS_TEMPLATE,content_type="application/xhtml+xml")

def test_import(request):
    mo_user = User.objects.get(uid=1)
    mo_shop = Shop.objects.get(sid=1)
    mo_bill = Bill.objects.get(bid=2)
    return HttpResponse(RFD.ImportOrders(mo_shop, mo_bill))
    #return JSONResponse({'xml':RFD.ImportOrders(mo_shop, mo_bill)})

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
