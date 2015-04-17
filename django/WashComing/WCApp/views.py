from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from WCLib.views import *
from WCApp.models import Android
from WCApp.forms import AppGetNewestAndroidForm
from WCApp.serializers import AndroidSerializer
from WCUser.models import User

# Create your views here.
@require_http_methods(['POST'])
def get_newest_android(request):
    fo_app = AppGetNewestAndroidForm(dict(request.GET.items() + request.POST.items()))
    if not fo_app.is_valid():
        return JSONResponse({'errmsg':fo_app.errors})
    d_data = fo_app.cleaned_data
    mo_android = Android.get_newest_version()
    if None == mo_android:
        JSONResponse({'errmsg':'db does not exist any version info'})
    se_android = AndroidSerializer(mo_android)
    d_response = se_android.data
    return JSONResponse(d_response)

def download(request):
    s_ios = ['iphone', 'ios']
    if any(s for s in s_ios if s in request.META['HTTP_USER_AGENT'].lower()):
        return HttpResponseRedirect('https://appsto.re/cn/PHiF4.i')
    if 'Android' in request.META['HTTP_USER_AGENT']:
        return HttpResponseRedirect('/media/android/xilaile.apk')
    return render_to_response('app/download.html')
