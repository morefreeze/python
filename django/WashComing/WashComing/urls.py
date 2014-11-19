from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WashComing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('WCUser.urls')),
    url(r'^bill/', include('WCBill.urls_bill')),
    url(r'^cart/', include('WCBill.urls_cart')),
    url(r'^cloth/', include('WCCloth.urls')),
    url(r'^logistics/', include('WCLogistics.urls_lg')),
    url(r'^address/', include('WCLogistics.urls_adr')),
)
