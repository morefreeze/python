# coding=utf-8
import base
import datetime as dt
import logging

from WCBill.models import Bill
from WCLogistics.models import RFD

logger = logging.getLogger('update_shop')
dt_today = dt.date.today()
dt_today = dt.datetime(year=dt_today.year, month=dt_today.month, day=dt_today.day)

a_to_get_bills = Bill.objects.filter(status__gte=Bill.WAITTING_GET, shop=None)
for it_bill in a_to_get_bills:
    mo_lg = it_bill.lg
    if None == mo_lg:
        continue
    mo_shop = RFD.tryFindShop(it_bill)
    if None != mo_shop:
        it_bill.shop = mo_shop
        it_bill.save()
        logger.info('find shop[%s] for bill[%s]' %(mo_shop, it_bill.bid))
    else:
        if it_bill.get_time_0 < dt_today:
            logger.error('the bill maybe not be got bid[%s] sl[%s]' %(it_bill.bid, mo_lg.get_order_no))

