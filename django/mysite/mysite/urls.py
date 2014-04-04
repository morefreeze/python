from django.conf.urls import patterns, include, url

from django.contrib import admin

from mysite.views import hello, current_datetime, fake_ssh
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^hello/$', hello),
    url(r'^time/$', current_datetime),
    url(r'^fake_ssh/$', fake_ssh),
)
