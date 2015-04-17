from django.conf.urls import patterns, url
from quiz.views import get_answer

urlpatterns = patterns(
    '',
    url(r'^get_answer$', get_answer),
)

