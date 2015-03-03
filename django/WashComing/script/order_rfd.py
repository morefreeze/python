# coding=utf-8
from __future__ import absolute_import
import base
from django.db.models import Min
from WCLogistics.models import OrderQueue, RFD
from WCBill.models import Bill
import json
import traceback
import datetime as dt
import sys
import logging

def handleAddFetchOrder(mo_queue, to_shop=True):
    try:
        mo_bill = mo_queue.bill
        d_res = RFD.AddFetchOrder(mo_bill, to_shop)
        print d_res
        if not d_res['IsSucceed']:
            mo_queue.message = json.dumps(d_res)
            return 1
        s_order_no = d_res['Message']
        mo_queue.message = d_res
        if '' == s_order_no:
            mo_queue.message = 'add fetch success, but order is empty'
            return 2
        mo_rfd = mo_bill.lg
        dt_now = dt.datetime.now()
        if None == mo_rfd:
            if to_shop:
                mo_rfd = RFD.objects.create(get_order_no=s_order_no,
                                            status=RFD.TO_GET,
                                           get_operate_time=dt_now)
            else:
                mo_rfd = RFD.objects.create(return_order_no=s_order_no,
                                            status=RFD.TO_RETURN,
                                           return_operate_time=dt_now)
            mo_bill.lg = mo_rfd
        else:
            if to_shop:
                mo_rfd.get_order_no = s_order_no
                mo_rfd.get_operate_time = dt_now
                mo_rfd.status = RFD.TO_GET
            else:
                mo_rfd.return_order_no = s_order_no
                mo_rfd.return_operate_time = dt_now
                mo_rfd.status = RFD.TO_RETURN
        if to_shop:
            mo_bill.change_status(Bill.WAITTING_GET)
        else:
            mo_bill.change_status(Bill.RETURNNING)
        mo_bill.save()
        mo_rfd.save()
    except Exception as e:
        logging.error(traceback.format_exc())
        mo_queue.message = traceback.format_exc()
        return 99
    return 0

def handleImportOrders(mo_queue, to_shop=False):
    try:
        mo_bill = mo_queue.bill
        d_res = RFD.ImportOrders(mo_bill, to_shop)
        print d_res
        if 'ResultCode' not in d_res or not d_res['ResultCode'].startswith('IsSuccess'):
            mo_queue.message = d_res.get('ResultMessage')
            return 1
        mo_rfd = mo_bill.lg
        s_way_no = d_res['WaybillNo']
        s_form_no = d_res['FormCode']
        dt_now = dt.datetime.now()
        if None == mo_rfd:
            mo_rfd = RFD.objects.create(return_way_no=s_way_no,
                                        return_form_no=s_form_no,
                                        return_operate_time=dt_now,
                                        status=RFD.TO_RETURN)
            mo_bill.lg = mo_rfd
        else:
            mo_rfd.return_way_no = s_way_no
            mo_rfd.return_form_no = s_form_no
            mo_rfd.return_operate_time = dt_now
            mo_rfd.status = RFD.TO_RETURN
        mo_bill.status = Bill.RETURNNING
        mo_rfd.save()
        mo_bill.save()
    except Exception as e:
        mo_queue.message = traceback.format_exc()
        return 99
    return 0

def handleImportGettingOrders(mo_queue):
    return handleImportOrders(mo_queue, to_shop=True)

def handleAddReturnningFetchOrder(mo_queue):
    return handleAddFetchOrder(mo_queue, to_shop=False)

if __name__ == '__main__':
    trigger_time = dt.datetime.now() + dt.timedelta(hours=8)
    if len(sys.argv) > 1:
        mo_queue = OrderQueue.objects.get(qid=sys.argv[1])
    else:
        mo_queue = OrderQueue.objects.all().filter(type__gt=0,status__lte=0,time__lt=trigger_time).order_by('update_time', 'type', 'time')
        if 0 == len(mo_queue):
            exit(0)
        mo_queue = mo_queue[0]
    print mo_queue.qid, mo_queue.bill.bid
    mo_queue.status = OrderQueue.DOING
    mo_queue.message = ''
    mo_queue.save()
    handle = {
        OrderQueue.AddFetchOrder: handleAddFetchOrder,
        OrderQueue.ImportGettingOrders: handleImportGettingOrders,
        OrderQueue.ImportOrders: handleImportOrders,
        OrderQueue.AddReturnningFetchOrder: handleAddReturnningFetchOrder,
    }
    i_ret_code = handle[mo_queue.type](mo_queue)
    if i_ret_code > 0:
        mo_queue.status = -i_ret_code
    else:
        mo_queue.status = OrderQueue.DONE
    mo_queue.save()
    if OrderQueue.DONE != mo_queue.status:
        exit(i_ret_code)
    exit(0)

