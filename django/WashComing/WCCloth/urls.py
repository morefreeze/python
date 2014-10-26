from django.conf.urls import patterns, url
from WCCloth.views import category, list, info

urlpatterns = patterns(
    '',
    url(r'^category$', category),
    url(r'^list$', list),
    url(r'^info$', info),
)
