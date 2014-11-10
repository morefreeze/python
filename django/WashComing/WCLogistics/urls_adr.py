from django.conf.urls import patterns, url
from WCLogistics.views import add, update, delete, list, set_default, info

urlpatterns = patterns(
    '',
    url(r'^add$', add),
    url(r'^update$', update),
    url(r'^delete$', delete),
    url(r'^list$', list),
    url(r'^set_default', set_default),
    url(r'^info$', info),
)
