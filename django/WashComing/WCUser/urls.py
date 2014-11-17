from django.conf.urls import patterns, url
from WCUser.views import register, login, info, update, active, \
        resend_active

urlpatterns = patterns(
    '',
    url(r'^register$', register),
    url(r'^login$', login),
    url(r'^info$', info),
    url(r'^update$', update),
    url(r'^resend_active$', resend_active),
    url(r'^active$', active),
)
