from django.conf.urls import patterns, url
from WCLogistics.views import list, info

urlpatterns = patterns(
    '',
    url(r'^list$', list),
    url(r'^info$', info),
)
