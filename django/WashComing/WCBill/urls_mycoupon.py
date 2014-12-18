from django.conf.urls import patterns, url
from WCBill.views import list_mycoupon

urlpatterns = patterns(
    '',
    url(r'^list$', list_mycoupon),
)
