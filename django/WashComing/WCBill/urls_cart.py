from django.conf.urls import patterns, url
from WCBill.views import submit_cart, list_cart

urlpatterns = patterns(
    '',
    url(r'^submit$', submit_cart),
    url(r'^list$', list_cart),
)
