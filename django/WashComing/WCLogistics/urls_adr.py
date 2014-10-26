from django.conf.urls import patterns, url
from WCLogistics.views import add, update, delete, set_default

urlpatterns = patterns(
    '',
    url(r'^add$', add),
    url(r'^update$', update),
    url(r'^delete$', delete),
    url(r'^set_default', set_default),
)
