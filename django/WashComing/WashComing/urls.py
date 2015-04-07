from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WashComing.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('WCUser.urls')),
    url(r'^bill/', include('WCBill.urls_bill')),
    url(r'^cart/', include('WCBill.urls_cart')),
    url(r'^mycoupon/', include('WCBill.urls_mycoupon')),
    url(r'^pay/', include('WCBill.urls_pay')),
    url(r'^cloth/', include('WCCloth.urls')),
    url(r'^logistics/', include('WCLogistics.urls_lg')),
    url(r'^address/', include('WCLogistics.urls_adr')),
    url(r'^app/', include('WCApp.urls')),
    url(r'^laundry/', include('WCLaundry.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
