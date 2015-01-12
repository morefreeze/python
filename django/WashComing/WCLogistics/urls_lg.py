from django.conf.urls import patterns, url
from WCLogistics.views import list_lg, info_lg, post_status

urlpatterns = patterns(
    '',
    #url(r'^list$', list_lg),
    #url(r'^info$', info_lg),
    url(r'^post_status$', post_status),
)
