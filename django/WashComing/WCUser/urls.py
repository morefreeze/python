from django.conf.urls import patterns, url
from WCUser.views import register, login, info, bind_email, update

urlpatterns = patterns(
    '',
    url(r'^register$', register),
    url(r'^login$', login),
    url(r'^info$', info),
    url(r'^bind_email$', bind_email),
    url(r'^update$', update),
)
