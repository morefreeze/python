# coding=utf-8
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from WCLib.views import *
from WCLib.models import *
from WCBill.serializers import BillSerializer, FeedbackSerializer, MyCouponSerializer
from WCBill.models import Bill, Feedback, Cart, Pingpp
from WCBill.forms import BillSubmitForm, BillListForm, BillInfoForm, BillCancelForm, \
        BillFeedbackForm, BillGetFeedbackForm
from WCBill.forms import CartSubmitForm, CartListForm
from WCBill.forms import MyCouponListForm, MyCouponCalcForm, MyCouponInfoForm, MyCouponAddForm
from WCUser.models import User
from WCBill.models import Bill, Coupon, MyCoupon, Pingpp_Charge, Pingpp_Refund
from WCLogistics.models import Address, OrderQueue
import json
import datetime as dt
import pingpp
import sys

# Create your views here.
@require_http_methods(['POST', 'GET'])
def submit(request):
    fo_bill = BillSubmitForm(dict(request.GET.items() + request.POST.items()))
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
        if d_data.get('payment') in ONLINE_PAYMENT:
            mo_bill.change_status(Bill.NOT_PAID)
        else:
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
# user's insurance, just record
    try:
        mo_bill.ext['insurance'] = float(d_data.get('insurance') or 0)
    except (Exception) as e:
        mo_bill.ext['insurance'] = 0.0
# minue user score
    mo_user.score -= i_score
    mo_user.save()
    i_use_coupon = mo_bill.ext.get('use_coupon')
    if i_use_coupon > 0:
# mark coupon used
        try:
            mo_mycoupon = MyCoupon.objects.get(mcid=i_use_coupon, used=False)
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
    d_response = {
        'errno':0,
        'bid':mo_bill.bid,
        'total':mo_bill.total,
    }
# request ping++ create charge
    if d_data.get('payment') in ONLINE_PAYMENT:
        s_client_ip = get_client_ip(request)
        mo_chr = Pingpp.create_charge(mo_bill, s_client_ip)
        d_response['charge'] = mo_chr
        if hasattr(mo_chr, 'id'):
            mo_bill.ext['charge_id'] = mo_chr.id
            mo_bill.save()
            mo_ping_chr = Pingpp_Charge.clone(mo_chr)
            if None == mo_ping_chr:
                logging.error('save Pingpp_Charge failed')
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def list(request):
    fo_bill = BillListForm(dict(request.GET.items() + request.POST.items()))
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
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

@require_http_methods(['POST', 'GET'])
def info(request):
    fo_bill = BillInfoForm(dict(request.GET.items() + request.POST.items()))
    if not fo_bill.is_valid():
        return JSONResponse({'errmsg':fo_bill.errors})
    d_data = fo_bill.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_bill = Bill.get_bill(mo_user.uid, d_data.get('bid'))
    if None == mo_bill:
        return JSONResponse({'errmsg':'bill not exist'})
    if eq_zero(mo_bill.total):
        mo_bill.calc_total()
        mo_bill.save()
    se_bill = BillSerializer(mo_bill)
    mo_chr = None
    if None != mo_bill.ext.get('charge_id') and eq_zero(mo_bill.paid):
        mo_chr = Pingpp.create_charge(mo_bill)
        if hasattr(mo_chr, 'id'):
            mo_bill.ext['charge_id'] = mo_chr.id
            mo_bill.save()
            mo_ping_chr = Pingpp_Charge.clone(mo_chr)
            if None == mo_ping_chr:
                logging.error('save Pingpp_Charge failed')
    se_bill.data['charge'] = mo_chr
    return JSONResponse(se_bill.data)

@require_http_methods(['POST', 'GET'])
def cancel(request):
    fo_bill = BillCancelForm(dict(request.GET.items() + request.POST.items()))
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
    if mo_bill.status >= Bill.GETTING:
        return JSONResponse({'errmsg':'bill status should not cancel'})
    mo_bill.cancel()
    return JSONResponse({'errno':0})

@require_http_methods(['POST', 'GET'])
def feedback(request):
    fo_bill = BillFeedbackForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def get_feedback(request):
    fo_bill = BillGetFeedbackForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def submit_cart(request):
    fo_bill = CartSubmitForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def list_cart(request):
    fo_bill = CartListForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def list_mycoupon(request):
    fo_mycoupon = MyCouponListForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def calc_mycoupon(request):
    fo_mycoupon = MyCouponCalcForm(dict(request.GET.items() + request.POST.items()))
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
        if it_mycoupon.is_vali_or_total(t_bill, b_report_error=False):
            se_mycoupon = MyCouponSerializer(it_mycoupon)
            #se_mycoupon.data['status'] = it_mycoupon.status
            d_response['data'].append(se_mycoupon.data)
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def info_mycoupon(request):
    fo_mycoupon = MyCouponInfoForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def add_mycoupon(request):
    fo_mycoupon = MyCouponAddForm(dict(request.GET.items() + request.POST.items()))
    if not fo_mycoupon.is_valid():
        return JSONResponse({'errmsg':fo_mycoupon.errors})
    d_data = fo_mycoupon.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    s_code = d_data.get('code')
    try:
        mo_coupon = Coupon.objects.get(use_code=True, code=s_code)
    except (Coupon.DoesNotExist) as e:
        logging.error('coupon code does not exist %s' %(s_code))
        return JSONResponse({'errmsg':'coupon code error'})
    if mo_coupon.is_valid():
        i_mcid = mo_coupon.add_user(mo_user)
    else:
        logging.error('coupon [%s] is not valid' %(mo_coupon.coid))
        return JSONResponse({'errmsg':'coupon [%s] is not valid' %(mo_coupon.coid)})
    try:
        mo_mycoupon = MyCoupon.objects.get(mcid=i_mcid, own=mo_user)
    except (MyCoupon.DoesNotExist) as e:
        return JSONResponse({'errmsg':'coupon not exist'})
    se_mycoupon = MyCouponSerializer(mo_mycoupon)
    se_mycoupon.data['errno'] = 0
    return JSONResponse(se_mycoupon.data)

@require_http_methods(['POST', 'GET'])
def ping_notify(request):
    try:
        js_notify = json.loads(request.body)
    except (Exception) as e:
        logging.error(e.__str__())
        return HttpResponse('fail')
    if 'object' not in js_notify:
        logging.error('object not in ping++ json')
        logging.error(js_notify)
        return HttpResponse('fail')
    if 'charge' == js_notify['object']:
        mo_ping_chr = Pingpp_Charge.clone(js_notify)
        if None == mo_ping_chr:
            return HttpResponse('fail')
        if mo_ping_chr.paid:
            try:
                mo_bill = Bill.objects.get(bid=mo_ping_chr.order_no)
                mo_bill.paid = mo_ping_chr.amount * 0.01
                mo_bill.change_status(Bill.CONFIRMING)
                mo_bill.save()
            except (Exception) as e:
                logging.error('no bill order_no[%s]' %(mo_ping_chr.order_no))
        logging.info('charge received chr_id[%s]' %(mo_ping_chr.id))
        return HttpResponse('success')
    elif 'refund' == js_notify['object']:
        mo_ping_re = Pingpp_Refund.clone(js_notify)
        if None == mo_ping_re:
            return HttpResponse('fail')
        if mo_ping_re.succeed:
            mo_ping_chr = mo_ping_re.charge
            try:
                mo_bill = Bill.objects.get(bid=mo_ping_chr.order_no)
                logging.debug(mo_bill)
                if mo_bill.paid < mo_ping_re.amount * 0.01:
                    logging.warning('bill paid less than refund paid[%.2f] amount[%d]' \
                        %(mo_bill.paid, mo_ping_re.amount))
                mo_bill.paid = max(0, mo_bill.paid - mo_ping_re.amount * 0.01)
                mo_bill.save()
            except (Exception) as e:
                logging.error('bill no exist [%s]' %(e))
        logging.info('refund received re_id[%s]' %(mo_ping_re.id))
        return HttpResponse('success')
    return HttpResponse('fail')

""" method template (12 lines)
@require_http_methods(['POST', 'GET'])
def submit(request):
    fo_bill = BillXXXXXForm(dict(request.GET.items() + request.POST.items()))
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
