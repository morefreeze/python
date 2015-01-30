from django.conf.urls import patterns, url
from WCBill.views import ping_notify

urlpatterns = patterns(
    '',
    url(r'^ping_notify$', ping_notify),
)
