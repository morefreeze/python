from django.shortcuts import render
from django.db.models import Max
from WCLib.views import *
from WCApp.models import Android
from WCApp.forms import AppGetNewestAndroidForm
from WCApp.serializers import AndroidSerializer
from WCUser.models import User

# Create your views here.
def get_newest_android(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_app = AppGetNewestAndroidForm(request.GET)
    if not fo_app.is_valid():
        return JSONResponse({'errmsg':fo_app.errors})
    d_data = fo_app.cleaned_data
    i_ver_code = Android.objects.all().aggregate(Max('ver_code'))['ver_code__max']
    if None == i_ver_code:
        return JSONResponse({'errmsg':'db does not exist any version info'})
    mo_android = Android.objects.get(ver_code=i_ver_code)
    se_android = AndroidSerializer(mo_android)
    d_response = se_android.data
    return JSONResponse(d_response)

