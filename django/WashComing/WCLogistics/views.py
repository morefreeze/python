from django.shortcuts import render

from WCLib.views import *
from WCLogistics.models import Address
from WCLogistics.forms import AddressAddForm, AddressUpdateForm, AddressDeleteForm, \
        AddressSetDefaultForm
from WCUser.models import User
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
    return JSONResponse({'errno':0})

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

#==============Map method
def list(request):
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

def info(request):
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
