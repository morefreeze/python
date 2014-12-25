from django.conf.urls import patterns, url
from WCBill.views import list_mycoupon, calc_mycoupon, info_mycoupon

urlpatterns = patterns(
    '',
    url(r'^list$', list_mycoupon),
    url(r'^calc$', calc_mycoupon),
    url(r'^info$', info_mycoupon),
)
