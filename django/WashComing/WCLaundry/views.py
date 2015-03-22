# coding=utf-8
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from WCLib.views import *
from WCLaundry.serializers import LaundrySerializer
from WCLaundry.forms import LaundryBillQueryForm, LaundryConfirmGetForm, LaundryGetBillsForm,\
        LaundryConfirmReturnForm
from WCBill.models import Bill
from WCBill.serializers import BillSerializer
from WCUser.models import Shop
from WCUser.serializers import ShopSerializer
from WCLogistics.models import OrderQueue
import datetime as dt

# Create your views here.
@require_http_methods(['POST'])
@login_required
def laundry_bill_query(request):
    mo_duser = request.user
    if None == mo_duser:
        import sys
        logging.error('%s need django user login' %(sys._getframe().f_code.co_name))
        return JSONResponse({'errmsg':'this method need login'})
    fo_laundry = LaundryBillQueryForm(dict(request.POST.items()))
    if not fo_laundry.is_valid():
        return JSONResponse({'errmsg':fo_laundry.errors})
    d_data = fo_laundry.cleaned_data
    i_bid = int(d_data.get('bid'))
    mo_user = request.user
    try:
        mo_bill = Bill.objects.get(bid=i_bid, status__gte=Bill.WAITTING_GET, status__lte=Bill.WASHING)
    except (Bill.DoesNotExist) as e:
        return JSONResponse({'errmsg':u'订单不存在或不需要确认状态'})
    se_bill = BillSerializer(mo_bill)
    return JSONResponse(se_bill.data)

@require_http_methods(['POST', 'GET'])
@login_required
def laundry_own_shops(request):
    mo_duser = request.user
    if None == mo_duser:
        import sys
        logging.error('%s need django user login' %(sys._getframe().f_code.co_name))
        return JSONResponse({'errmsg':'this method need login'})
    a_shops = Shop.objects.filter(own=mo_duser)
    d_response = {}
    d_response['data'] = []
    for it_shop in a_shops:
        se_shop = ShopSerializer(it_shop)
        d_response['data'].append(se_shop.data)
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST'])
@login_required
def laundry_confirm_get(request):
    mo_duser = request.user
    if None == mo_duser:
        import sys
        logging.error('%s need django user login' %(sys._getframe().f_code.co_name))
        return JSONResponse({'errmsg':'this method need login'})
    d_response = {}
    fo_laundry = LaundryConfirmGetForm(dict(request.POST.items()))
    if not fo_laundry.is_valid():
        return JSONResponse({'errmsg':fo_laundry.errors})
    d_data = fo_laundry.cleaned_data
    s_bid = d_data.get('bid')
    s_sid = d_data.get('sid')
    s_comment = d_data.get('shop_comment') or ''
    try:
        mo_bill = Bill.objects.get(bid=s_bid, deleted=False)
    except (Bill.DoesNotExist) as e:
        logging.error('bill id not exist or deleted %s' %(s_bid))
        return JSONResponse({'errmsg': u'确认失败！订单号不存在或已删除'})
    if mo_bill.status not in (Bill.WAITTING_GET, Bill.GETTING, Bill.WASHING):
        logging.error('bill status is error bid[%s] status[%s]' %(s_bid, mo_bill.status))
        return JSONResponse({'errmsg': u'确认失败！该订单号当前不需要确认'})
    try:
        mo_shop = Shop.objects.get(sid=s_sid, deleted=False)
    except (Shop.DoesNotExist) as e:
        logging.error('shop id not exist or deleted %s' %(s_sid))
        return JSONResponse({'errmsg': u'确认失败！店铺号不存在或已删除'})
    if mo_shop.own != mo_duser:
        logging.error('shop not belong to user sid[%s] duser[%s]' %(s_sid, mo_duser))
        return JSONResponse({'errmsg': u'确认失败！该店铺不在当前账号下，请尝试重新登陆'})
    if None != mo_bill.shop and mo_bill.shop != mo_shop:
        logging.error('bill has a shop bid[%s] old_sid[%s] new_sid[%s]' %(s_bid, mo_bill.shop_id, s_sid))
        return JSONResponse({'errmsg': u'确认失败！该订单已经被其它店铺确认'})
    mo_bill.shop = mo_shop
    mo_bill.change_status(Bill.WASHING)
    mo_bill.shop_comment = s_comment
    mo_bill.save()
    logging.info('shop confirm get clothes success bid[%s]' %(s_bid))
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST'])
@login_required
def laundry_get_bills(request):
    mo_duser = request.user
    if None == mo_duser:
        import sys
        logging.error('%s need django user login' %(sys._getframe().f_code.co_name))
        return JSONResponse({'errmsg':'this method need login'})
    d_response = {}
    fo_laundry = LaundryGetBillsForm(dict(request.POST.items()))
    if not fo_laundry.is_valid():
        return JSONResponse({'errmsg':fo_laundry.errors})
    d_data = fo_laundry.cleaned_data
    s_method = d_data.get('method')
    i_page = int(d_data.get('page') or 1)
    i_page -= 1
    if i_page < 0:
        i_page = 0
# each page 50 item
    RN = 10
    i_offset = i_page * RN
    i_limit = (i_page+1) * RN
    if 'to_send' == s_method:
        a_bills = Bill.objects.filter(shop__own=mo_duser, status=Bill.WASHING)[i_offset:i_limit]
    elif 'sent' == s_method:
        a_bills = Bill.objects.filter(shop__own=mo_duser, status__gt=Bill.WASHING)[i_offset:i_limit]
    else:
        logging.error('method error %s' %(s_method))
        return JSONResponse({'errmsg': 'method error'})
    d_response['data'] = []
    for it_bill in a_bills:
        se_bill = BillSerializer(it_bill)
        d_response['data'].append(se_bill.data)
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST'])
@login_required
def laundry_confirm_return(request):
    mo_duser = request.user
    if None == mo_duser:
        import sys
        logging.error('%s need django user login' %(sys._getframe().f_code.co_name))
        return JSONResponse({'errmsg':'this method need login'})
    d_response = {}
    fo_laundry = LaundryConfirmReturnForm(dict(request.POST.items()))
    if not fo_laundry.is_valid():
        return JSONResponse({'errmsg':fo_laundry.errors})
    d_data = fo_laundry.cleaned_data
    s_bid = d_data.get('bid')
    s_comment = d_data.get('shop_comment') or ''
    try:
        mo_bill = Bill.objects.get(bid=s_bid, deleted=False)
    except (Bill.DoesNotExist) as e:
        logging.error('bill id not exist or deleted %s' %(s_bid))
        return JSONResponse({'errmsg': u'确认失败！订单号不存在或已删除'})
    if Bill.WASHING != mo_bill.status:
        logging.error('bill status is error bid[%s] status[%s]' %(s_bid, mo_bill.status))
        return JSONResponse({'errmsg': u'确认失败！该订单号当前不需要确认'})
    mo_bill.change_status(Bill.RETURNNING)
    mo_bill.shop_comment = s_comment
    mo_bill.save()
# create or change orderqueue return order to send right now
    a_oq = OrderQueue.objects.filter(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder, status=OrderQueue.TODO)
    dt_now = dt.datetime.now()
    if 0 == len(a_oq):
        logging.error('orderqueue do not exist bill %s' %(s_bid))
        mo_oq = OrderQueue.objects.create(bill=mo_bill, type=OrderQueue.AddReturnningFetchOrder, status=OrderQueue.TODO, \
                                            time=dt_now)
    else:
        if len(a_oq) > 1:
            logging.warning('orderqueue find more todo return order %s' %(s_bid))
        mo_oq = a_oq[0]
        mo_oq.time = dt_now
    mo_oq.save()
    d_response['errno'] = 0
    return JSONResponse(d_response)

""" method template (11 lines)
@require_http_methods(['POST', 'GET'])
def info(request):
    fo_cloth = ClothXXXXXForm(dict(request.GET.items() + request.POST.items()))
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = Cloth.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
"""
