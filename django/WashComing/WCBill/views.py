# coding=utf-8
from django.shortcuts import render
from WCLib.views import *
from WCBill.serializers import BillSerializer
from WCBill.models import Bill
from WCBill.forms import BillSubmitForm, BillListForm, BillInfoForm, BillCancelForm
from WCUser.models import User
from WCLogistics.models import Address

from datetime import datetime

# Create your views here.
def submit(request):
    if request.method == 'GET':
        fo_bill = BillSubmitForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            mo_bill = Bill()
            mo_bill.bid = None
            mo_bill.create_time = None
            mo_bill.get_time_0 = d_data.get('get_time_0')
            mo_bill.get_time_1 = d_data.get('get_time_1')
            mo_bill.return_time_0 = d_data.get('return_time_0')
            mo_bill.return_time_1 = d_data.get('return_time_1')
            mo_bill.own = mo_user
            mo_bill.lg = None
            mo_adr = Address.get_adr(mo_user.uid, d_data.get('aid'))
            if None == mo_adr:
                return JSONResponse({'errmsg':'address error'})
            mo_bill.adr = mo_adr
            mo_bill.status = 0
            mo_bill.deleted = 0
            mo_bill.clothes = d_data.get('clothes')
            mo_bill.ext = None
            mo_bill.save()
            se_bill = BillSerializer(mo_bill)
            return JSONResponse({'errno':0, 'bid':se_bill.data.get('bid')})
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})

def list(request):
    if request.method == 'GET':
        fo_bill = BillListForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            i_pn = d_data.get('pn')
            i_rn = 5
            i_deleted = d_data.get('deleted')
            i_offset = (i_pn-1)*i_rn
            i_limit = i_rn
            # todo: order rule
            if i_delete == 2:
# query all include deleted
                a_bills = Bill.objects.filter(own=mo_user)\
                    .order_by('get_time_0', 'return_time_0', '-bid')[i_offset:i_offset+i_limit]
            else:
                a_bills = Bill.objects.filter(own=mo_user,deleted=i_deleted)\
                    .order_by('get_time_0', 'return_time_0', '-bid')[i_offset:i_offset+i_limit]
            d_response = dict()
            d_response['errno'] = 0
            d_response['data'] = []
            for mo_bill in a_bills:
                d_response['data'].append(BillSerializer(mo_bill).data)
            d_response['count'] = len(d_response['data'])
            return JSONResponse(d_response)
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})

def info(request):
    if request.method == 'GET':
        fo_bill = BillInfoForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
            se_bill = BillSerializer(mo_bill)
            return JSONResponse(se_bill.data)
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})

def cancel(request):
    if request.method == 'GET':
        fo_bill = BillCancelForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
            if None == mo_bill:
                return JSONResponse({'errmsg':'bill not exist'})
            mo_bill.deleted = 1
            mo_bill.save()
            return JSONResponse({'errno':0})
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})

""" method template (13 lines)
def submit(request):
    if request.method == 'GET':
        fo_bill = BillXXXXXForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            mo_bill = Bill()
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})
"""
