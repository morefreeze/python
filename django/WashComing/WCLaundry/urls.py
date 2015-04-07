from django.conf.urls import patterns, url
from WCLaundry.views import laundry_bill_query, laundry_own_shops, laundry_confirm_get, \
        laundry_get_total_pages, laundry_get_bills, laundry_confirm_return
urlpatterns = patterns(
    '',
    url(r'^bill_query$', laundry_bill_query),
    url(r'^own_shops$', laundry_own_shops),
    url(r'^confirm_get$', laundry_confirm_get),
    url(r'^get_total_pages$', laundry_get_total_pages),
    url(r'^get_bills$', laundry_get_bills),
    url(r'^confirm_return$', laundry_confirm_return),
)
