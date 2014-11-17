# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator
from WCLib.views import *
from WCBill.serializers import BillSerializer
from WCBill.models import Bill
from WCBill.forms import BillSubmitForm, BillListForm, BillInfoForm, BillCancelForm, \
        BillSendFeedbackForm
from WCUser.models import User
from WCLogistics.models import Address
import json

from datetime import datetime

# Create your views here.
def submit(request):
    if request.method == 'GET':
        fo_bill = BillSubmitForm(request.GET)
        if not fo_bill.is_valid():
            return JSONResponse({'errmsg':fo_bill.errors})
        d_data = fo_bill.cleaned_data
        s_name = d_data.get('username')
        s_token = d_data.get('token')
        mo_user = User.get_user(s_name, s_token)
        if None == mo_user:
            return JSONResponse({'errmsg':'username or password or permission error'})
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
        mo_bill.address = mo_adr.get_full_address()
        mo_bill.real_name = mo_adr.real_name
        mo_bill.phone = mo_adr.phone
        mo_bill.status = 0
        mo_bill.deleted = 0
        mo_bill.ext = None
        mo_bill.clothes = mo_bill.format_cloth(d_data.get('clothes'))
        mo_bill.comment = d_data.get('comment')
        i_score = d_data.get('score', 0)
        if None == i_score:
            i_score = 0
        if i_score < 0 or mo_user.score < i_score:
            return JSONResponse({'errmsg':'score error'})
        mo_bill.score = i_score
        mo_bill.calc_total()
        s_errmsg = mo_bill.ext.get('error')
        mo_bill.save()
        if None != s_errmsg and '' != s_errmsg:
            mo_bill.deleted = True
            mo_bill.status = -20
            mo_bill.save()
            return JSONResponse({'errmsg': 'some error happen, please contact admin'})
        mo_user.score -= i_score
        mo_user.save()
        se_bill = BillSerializer(mo_bill)
        return JSONResponse({'errno':0, 'bid':se_bill.data.get('bid'),
                             'total':se_bill.data.get('total')})
    return JSONResponse({'errmsg':'method error'})

def list(request):
    if request.method == 'GET':
        fo_bill = BillListForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token, is_active=False)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            i_pn = d_data.get('pn')
            if None == i_pn:
                i_pn = 1
            i_rn = 5
            i_deleted = d_data.get('deleted')
            i_offset = (i_pn-1)*i_rn
            i_limit = i_rn
            # todo: order rule
            if i_deleted == 2:
# query all include deleted
                a_bills = Bill.objects.filter(own=mo_user)\
                    .order_by('get_time_0', 'return_time_0', '-bid')#[i_offset:i_offset+i_limit]
            else:
                a_bills = Bill.objects.filter(own=mo_user,deleted=i_deleted)\
                    .order_by('get_time_0', 'return_time_0', '-bid')#[i_offset:i_offset+i_limit]
            try:
                paginator = Paginator(a_bills, i_rn)
                p_bills = paginator.page(i_pn)
            except EmptyPage:
                p_bills = list()
            d_response = dict()
            d_response['errno'] = 0
            d_response['data'] = []
            for mo_bill in p_bills.object_list:
                d_response['data'].append(BillSerializer(mo_bill).data)
            d_response['pages'] = paginator.page_range
            d_response['cur_page'] = p_bills.number
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
            mo_user = User.get_user(s_name, s_token, is_active=False)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password error'})
            mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
            if None == mo_bill:
                return JSONResponse({'errmsg':'bill not exist'})
            if eq_zero(mo_bill.total):
                mo_bill.calc_total()
                mo_bill.save()
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
                return JSONResponse({'errmsg':'username or password or permission error'})
            mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
            if None == mo_bill:
                return JSONResponse({'errmsg':'bill not exist'})
            s_errmsg = mo_bill.ext.get('error')
            if None == s_errmsg or '' == s_errmsg and mo_bill.score > 0:
                mo_user.score += mo_bill.score
            mo_bill.status = -10
            mo_bill.save()
            return JSONResponse({'errno':0})
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})

def send_feedback(request):
    if request.method == 'GET':
        fo_bill = BillSendFeedbackForm(request.GET)
        if fo_bill.is_valid():
            d_data = fo_bill.cleaned_data
            s_name = d_data.get('username')
            s_token = d_data.get('token')
            mo_user = User.get_user(s_name, s_token)
            if None == mo_user:
                return JSONResponse({'errmsg':'username or password or permission error'})
            mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
            if None == mo_bill:
                return JSONResponse({'errmsg':'bill not exist'})
            mo_bill.feedback = d_data.get('feedback')
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
                return JSONResponse({'errmsg':'username or password or permission error'})
            mo_bill = Bill()
        return JSONResponse({'errmsg':fo_bill.errors})
    return JSONResponse({'errmsg':'method error'})
"""
