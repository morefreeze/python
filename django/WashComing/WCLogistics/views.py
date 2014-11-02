# coding=utf-8
from django.shortcuts import render

from WCLib.views import *
from WCLogistics.models import Address
from WCLogistics.forms import AddressAddForm, AddressUpdateForm, AddressDeleteForm, \
        AddressListForm, AddressSetDefaultForm
from WCLogistics.serializers import AddressSerializer
from WCUser.models import User
from WCUser.serializers import UserSerializer
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
    if '' != d_data.get('provice'):
        mo_adr.provice = d_data.get('provice')
    if '' != d_data.get('city'):
        mo_adr.city = d_data.get('city')
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

#==============RFD method
def lg_list(request):
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

def lg_info(request):
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
    s_s = request.GET.get('s')
    return JSONResponse({'res':sign_data(s_s)})

def sign_data(js_data):
    if None == js_data:
        return None
    s_hash = base64.b64encode(hashlib.md5(js_data).digest())
    pk_prikey = ct.load_privatekey(ct.FILETYPE_PEM, open('rfd.pem').read())
    s_res = base64.b64encode(ct.sign(pk_prikey, s_hash, 'sha1'))
    return s_res

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
