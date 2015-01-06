# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator
from WCLib.views import *
from WCBill.serializers import BillSerializer, FeedbackSerializer, MyCouponSerializer
from WCBill.models import Bill, Feedback, Cart
from WCBill.forms import BillSubmitForm, BillListForm, BillInfoForm, BillCancelForm, \
        BillFeedbackForm, BillGetFeedbackForm
from WCBill.forms import CartSubmitForm, CartListForm
from WCBill.forms import MyCouponListForm, MyCouponCalcForm, MyCouponInfoForm
from WCUser.models import User
from WCBill.models import Bill, Coupon, MyCoupon
from WCLogistics.models import Address, OrderQueue
import json
import datetime as dt

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
    dt_now = dt.datetime.now()
    # reserve bill will check get_time
    if not d_data.get('immediate'):
        if mo_bill.get_time_1 <= mo_bill.get_time_0 or mo_bill.get_time_0 <= dt_now:
            return JSONResponse({'errmsg':'get_time error'})
    mo_bill.return_time_0 = d_data.get('return_time_0')
    mo_bill.return_time_1 = d_data.get('return_time_1')
    if mo_bill.return_time_1 <= mo_bill.return_time_0:
        return JSONResponse({'errmsg':'return_time error'})
    if mo_bill.return_time_0 < mo_bill.get_time_0+dt.timedelta(days=4):
        return JSONResponse({'errmsg':'return_time error'})
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
    mo_bill.deleted = 0
    mo_bill.ext = {}
    mo_bill.ext['payment'] = d_data.get('payment')
    mo_bill.clothes = mo_bill.format_cloth(d_data.get('clothes'))
    mo_bill.comment = d_data.get('comment')
    i_score = d_data.get('score', 0)
    if None == i_score:
        i_score = 0
    if i_score < 0 or mo_user.score < i_score:
        return JSONResponse({'errmsg':'score error'})
    mo_bill.score = i_score
    mo_bill.ext['use_coupon'] = d_data.get('mcid')
# above all init for calc_total

    mo_bill.calc_total()

# if no inquiry cloth will confirm directly
# immediate send order after client helper confirm
    if d_data.get('immediate'):
        mo_bill.ext['immediate'] = True
# every bill custom helper SHOULD confirm
    if True or mo_bill.is_inquiry():
        mo_bill.change_status(Bill.CONFIRMING)
    else:
        mo_bill.change_status(Bill.WAITTING_GET)
    a_errmsg = mo_bill.ext.get('error')
    mo_bill.save()
    if len(a_errmsg or []) > 0:
        mo_bill.deleted = True
        mo_bill.change_status(Bill.ERROR)
        mo_bill.save()
        return JSONResponse({'errmsg': 'some error happened, please contact admin'})
# minue user score
    mo_user.score -= i_score
    mo_user.save()
    i_use_coupon = mo_bill.ext.get('use_coupon')
    if i_use_coupon > 0:
# mark coupon used
        try:
            mo_mycoupon = MyCoupon.objects.get(mcid=i_use_coupon)
            mo_mycoupon.used = True
            mo_mycoupon.save()
        except (MyCoupon.DoesNotExist) as e:
            mo_bill.add_error(e.__str__())
            mo_bill.save()
# remove cart seltcted clothes
    Cart.remove_bill_clothes(mo_user, mo_bill)
# add order push queue
# if no need client helper confirm then send order queue directly
# or send it after client helper confirm
    if False and mo_bill.status == Bill.WAITTING_GET:
        dt_fetch_time = mo_bill.get_time_0
        OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddFetchOrder,
                                  status=OrderQueue.TODO, time=dt_fetch_time)
        dt_import_time = mo_bill.return_time_0
        OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder,
                                  status=OrderQueue.TODO, time=dt_import_time)
    return JSONResponse({'errno':0, 'bid':mo_bill.bid,
                         'total':mo_bill.total})

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
        p_bills = []
    d_response = {}
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
    if mo_bill.status >= Bill.GETTING:
        return JSONResponse({'errmsg':'bill status should not cancel'})
    s_errmsg = mo_bill.ext.get('error')
    if None == s_errmsg or '' == s_errmsg and mo_bill.score > 0:
        mo_user.score += mo_bill.score
    mo_bill.change_status(Bill.USER_CANCEL)
    mo_bill.save()
# remove order push
    a_orderqueue = OrderQueue.objects.filter(bill=mo_bill, status__lte=OrderQueue.TODO)
    for it_orderqueue in a_orderqueue:
        it_orderqueue.status = OrderQueue.NO_DO_BUT_DONE
        it_orderqueue.save()
# return coupon
    if mo_bill.ext.get('use_mycoupon'):
        try:
            mo_mycoupon = MyCoupon.objects.get(mcid=mo_bill.ext.get('use_mycoupon'))
            if mo_mycoupon.used:
                mo_mycoupon.used = False
        except (MyCoupon.DoesNotExist) as e:
            mo_bill.add_error(e.__str__())
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
    if Bill.NEED_FEEDBACK != mo_bill.status:
        return JSONResponse({'errmsg':'bill do not need feedback'})
    i_rate = d_data.get('rate')
    s_content = d_data.get('content')
    if None == s_content:
        s_content = ''
    mo_fb, created = Feedback.objects.get_or_create(bill=mo_bill)
    mo_fb.rate = i_rate
    mo_fb.content = s_content
    mo_fb.save()
    mo_bill.change_status(Bill.DONE)
    mo_bill.save()
    if mo_bill.total > 0:
        mo_user.exp += int(mo_bill.total)
        mo_user.score += int(mo_bill.total)
        mo_user.save()
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
    mo_cart.clear_ext()
    mo_cart.clothes = mo_cart.format_cloth(d_data.get('clothes'))
    mo_cart.save()
    if mo_cart.ext.get('error'):
        return JSONResponse({'errmsg':'some error happened, please contact admin'})
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
    d_response = {}
    d_response['errno'] = 0
# keep interface consistency
    d_response['data'] = mo_cart.clothes
    d_response['clothes'] = mo_cart.clothes
    return JSONResponse(d_response)

def list_mycoupon(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_mycoupon = MyCouponListForm(request.GET)
    if not fo_mycoupon.is_valid():
        return JSONResponse({'errmsg':fo_mycoupon.errors})
    d_data = fo_mycoupon.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    i_type = d_data.get('type')
    dt_now = dt.datetime.now()
    a_mycoupons = MyCoupon.query_mycoupons(mo_user, i_type)
    d_response = {
        'data': [],
        'errno': 0,
    }
    for it_mycoupon in a_mycoupons:
        se_mycoupon = MyCouponSerializer(it_mycoupon)
        d_response['data'].append(se_mycoupon.data)
    return JSONResponse(d_response)

def calc_mycoupon(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_mycoupon = MyCouponCalcForm(request.GET)
    if not fo_mycoupon.is_valid():
        return JSONResponse({'errmsg':fo_mycoupon.errors})
    d_data = fo_mycoupon.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    s_clothes = d_data.get('clothes')
    a_mycoupons = MyCoupon.query_mycoupons(mo_user, MyCoupon.CAN_USE)
    d_response = {
        'data': [],
        'errno': 0,
    }
    mo_bill = Bill()
    mo_bill.clothes = json.loads(s_clothes)
    mo_bill.format_cloth()
    for it_mycoupon in a_mycoupons:
        t_bill = Bill(clothes=mo_bill.clothes, own=mo_user)
        if it_mycoupon.is_vali(t_bill, b_report_error=False):
            se_mycoupon = MyCouponSerializer(it_mycoupon)
            #se_mycoupon.data['status'] = it_mycoupon.status
            d_response['data'].append(se_mycoupon.data)
    return JSONResponse(d_response)

def info_mycoupon(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_mycoupon = MyCouponInfoForm(request.GET)
    if not fo_mycoupon.is_valid():
        return JSONResponse({'errmsg':fo_mycoupon.errors})
    d_data = fo_mycoupon.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    i_mcid = d_data.get('mcid')
    try:
        mo_mycoupon = MyCoupon.objects.get(mcid=i_mcid, own=mo_user)
    except (MyCoupon.DoesNotExist) as e:
        return JSONResponse({'errmsg':'coupon not exist'})
    se_mycoupon = MyCouponSerializer(mo_mycoupon)
    return JSONResponse(se_mycoupon.data)

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
