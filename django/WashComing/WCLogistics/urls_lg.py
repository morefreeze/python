from django.conf.urls import patterns, url
from WCLogistics.views import list_lg, info_lg, test_order, test_post_status, test_import

urlpatterns = patterns(
    '',
    url(r'^list$', list_lg),
    url(r'^info$', info_lg),
    url(r'^test_order$', test_order),
    url(r'^test_post_status$', test_post_status),
    url(r'^test_import$', test_import),
)
