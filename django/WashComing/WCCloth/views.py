from django.db import IntegrityError
from django.shortcuts import render
from WCLib.views import *
from WCUser.models import User
from WCCloth.serializers import ClothSerializer
from WCCloth.models import Cloth
from WCCloth.forms import ClothCategoryForm, ClothListForm, ClothInfoForm

# Create your views here.

def category(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_cloth = ClothCategoryForm(request.GET)
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    a_category = Cloth.get_category()
    d_response = dict()
    d_response['data'] = []
    if None != a_category:
        for it_category in a_category:
            d_response['data'].append(ClothSerializer(it_category).data)
    d_response['errno'] = 0
    return JSONResponse(d_response)

def list(request):
    if request.method == 'GET':
        fo_cloth = ClothLoginForm(request.GET)
        if fo_cloth.is_valid():
            mo_user = Cloth.create(fo_cloth.cleaned_data)
            mo_user = mo_user.vali_passwd(fo_cloth.cleaned_data)
        return JSONResponse({'errmsg':fo_cloth.errors})
    return JSONResponse({'errmsg':'method error'})

def info(request):
    if request.method == 'GET':
        fo_cloth = ClothInfoForm(request.GET)
        if fo_cloth.is_valid():
            s_name = fo_cloth.cleaned_data.get('username')
            s_token = fo_cloth.cleaned_data.get('token')
            try:
                mo_user = Cloth.objects.get(name=s_name, token=s_token)
                se_user = ClothSerializer(mo_user)
                d_response = dict()
                d_response['uid'] = se_user.data['uid']
                d_response['username'] = se_user.data['name']
                d_response['token'] = se_user.data['token']
                d_response['score'] = se_user.data['score']
                d_response['level'] = Cloth.gen_level(d_response['score'])
                d_response['errno'] = 0
                return JSONResponse(d_response)
            except (Cloth.DoesNotExist) as e:
                return JSONResponse({'errmsg':'username or token error'})
        return JSONResponse({'errmsg':fo_cloth.errors})
    return JSONResponse({'errmsg':'method error'})

def bind_email(request):
    if request.method == 'GET':
        fo_cloth = ClothBindEmailForm(request.GET)
        if fo_cloth.is_valid():
            s_name = fo_cloth.cleaned_data.get('username')
            s_token = fo_cloth.cleaned_data.get('token')
            s_email = fo_cloth.cleaned_data.get('email')
            try:
                mo_user = Cloth.objects.get(name=s_name, token=s_token)
                mo_user.email = s_email
                mo_user.save()
                d_response = {'errno':0}
                return JSONResponse(d_response)
            except (Cloth.DoesNotExist) as e:
                return JSONResponse({'errmsg':'username or token error'})
        return JSONResponse({'errmsg':fo_cloth.errors})
    return JSONResponse({'errmsg':'method error'})

""" method template (7 lines)
def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_cloth = ClothXXXXXForm(request.GET)
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    mo_cloth = Cloth.create(fo_cloth.cleaned_data)
"""
