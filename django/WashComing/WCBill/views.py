# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator
from WCLib.views import *
from WCBill.serializers import BillSerializer, FeedbackSerializer
from WCBill.models import Bill, Feedback, Cart
from WCBill.forms import BillSubmitForm, BillListForm, BillInfoForm, BillCancelForm, \
        BillFeedbackForm, BillGetFeedbackForm
from WCBill.forms import CartSubmitForm, CartListForm
from WCUser.models import User
from WCLogistics.models import Address
import json

from datetime import datetime

# Create your views here.
def submit(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillSubmitForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token, is_active=True)
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
    mo_bill.province = mo_adr.province
    mo_bill.city = mo_adr.city
    mo_bill.area = mo_adr.area
    mo_bill.address = mo_adr.address
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
    Cart.clean(mo_user)
    se_bill = BillSerializer(mo_bill)
    return JSONResponse({'errno':0, 'bid':se_bill.data.get('bid'),
                         'total':se_bill.data.get('total')})

def list(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillListForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token, is_active=True)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    i_pn = d_data.get('pn')
    if None == i_pn:
        i_pn = 1
    i_rn = 5
    i_deleted = d_data.get('deleted')
    i_offset = (i_pn-1)*i_rn
    i_limit = i_rn
    if i_deleted == 2:
# query all include deleted
        a_bills = Bill.objects.filter(own=mo_user)\
            .order_by('-bid')#[i_offset:i_offset+i_limit]
    else:
        a_bills = Bill.objects.filter(own=mo_user,deleted=i_deleted)\
            .order_by('-bid')#[i_offset:i_offset+i_limit]
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

def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillInfoForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token, is_active=True)
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

def cancel(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillCancelForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token, is_active=True)
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

def feedback(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillFeedbackForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
    if None == mo_bill:
        return JSONResponse({'errmsg':'bill not exist'})
    i_rate = d_data.get('rate')
    s_content = d_data.get('content')
    if None == s_content:
        s_content = ''
    mo_fb, created = Feedback.objects.get_or_create(bill=mo_bill, create_time=None, rate=i_rate, content=s_content)
    return JSONResponse({'fid':mo_fb.fid, 'errno':0})

def get_feedback(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillGetFeedbackForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
    if None == mo_bill:
        return JSONResponse({'errmsg':'bill not exist'})
    mo_fb = Feedback.objects.get(bill=mo_bill)
    se_fb = FeedbackSerializer(mo_fb)
    d_response = se_fb.data
    d_response['errno'] = 0
    return JSONResponse(d_response)

def submit_cart(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = CartSubmitForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    mo_cart, created = Cart.objects.get_or_create(own=mo_user)
    mo_cart.clothes = mo_cart.format_cloth(d_data.get('clothes'))
    mo_cart.save()
    return JSONResponse({'caid':mo_cart.caid, 'errno':0})

def list_cart(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = CartListForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    mo_cart, created = Cart.objects.get_or_create(own=mo_user)
    d_response = dict()
    d_response['errno'] = 0
    d_response['clothes'] = mo_cart.clothes
    return JSONResponse(d_response)

""" method template (13 lines)
def submit(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_bill = BillXXXXXForm(request.GET)
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    mo_bill = Bill()
"""
