from django.conf.urls import patterns, url
from WCLogistics.views import lg_list, lg_info, test_sign

urlpatterns = patterns(
    '',
    url(r'^list$', lg_list),
    url(r'^info$', lg_info),
    url(r'^test_sign$', test_sign),
)
