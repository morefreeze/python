from django.conf.urls import patterns, url
from WCBill.views import submit, list, info, cancel

urlpatterns = patterns(
    '',
    url(r'^submit$', submit),
    url(r'^list$', list),
    url(r'^info$', info),
    url(r'^cancel$', cancel),
)