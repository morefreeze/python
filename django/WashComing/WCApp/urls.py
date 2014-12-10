from django.conf.urls import patterns, url
from WCApp.views import get_newest_android, download

urlpatterns = patterns(
    '',
    url(r'^get_newest_android$', get_newest_android),
    url(r'^download$', download),
)

