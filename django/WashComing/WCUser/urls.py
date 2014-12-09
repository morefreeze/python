from django.conf.urls import patterns, url
from WCUser.views import register, login, info, update, change_password, active, \
        resend_active, resend_reset, reset_password, reset_password_confirm, reset_password_complete, \
        feedback, upload_avatar, third_bind, third_login, bind_email

urlpatterns = patterns(
    '',
    url(r'^register$', register),
    url(r'^login$', login),
    url(r'^info$', info),
    url(r'^update$', update),
    url(r'^change_password$', change_password),
    url(r'^resend_active$', resend_active),
    url(r'^active$', active),
    url(r'^reset_password$', reset_password),
    url(r'^resend_reset$', resend_reset),
    url(r'^reset_password_confirm', reset_password_confirm),
    url(r'^reset_password_complete', reset_password_complete),
    url(r'^feedback$', feedback),
    url(r'^upload_avatar$', upload_avatar),
    #url(r'^admin_upload_avatar$', admin_upload_avatar, name='admin_upload_avatar'),
    url(r'^third_bind$', third_bind),
    url(r'^third_login$', third_login),
    url(r'^bind_email$', bind_email),
)
