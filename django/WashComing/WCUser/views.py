from django.db import IntegrityError
from django.shortcuts import render
from WCLib.views import *
from WCUser.serializers import UserSerializer
from WCUser.models import User
from WCUser.forms import UserRegisterForm, UserLoginForm, UserInfoForm, UserBindEmailForm

# Create your views here.

def register(request):
    if request.method == 'GET':
        fo_user = UserRegisterForm(request.GET)
        if fo_user.is_valid():
            mo_user = User.create(fo_user.cleaned_data)
            s_token = mo_user.gen_token(fo_user.cleaned_data)
            mo_user.token = s_token
            try:
                mo_user.save()
                se_user = UserSerializer(mo_user)
                return JSONResponse(se_user.data)
# duplicate username
            except IntegrityError as e:
                return JSONResponse({'errmsg':'username has been registered'})
        return JSONResponse({'errmsg':fo_user.errors})
    return JSONResponse({'errmsg':'method error'})

def login(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
        fo_user = UserLoginForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    se_user = UserSerializer(mo_user)
    d_response = dict()
    d_response['uid'] = se_user.data['uid']
    d_response['username'] = se_user.data['name']
    d_response['token'] = se_user.data['token']
    d_response['errno'] = 0
    return JSONResponse(d_response)

def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserInfoForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    s_name = fo_user.cleaned_data.get('username')
    s_token = fo_user.cleaned_data.get('token')
    try:
        mo_user = User.objects.get(name=s_name, token=s_token)
        se_user = UserSerializer(mo_user)
        d_response = dict()
        d_response['uid'] = se_user.data['uid']
        d_response['username'] = se_user.data['name']
        d_response['token'] = se_user.data['token']
        d_response['score'] = se_user.data['score']
        d_response['level'] = User.gen_level(d_response['score'])
        d_response['errno'] = 0
        return JSONResponse(d_response)
    except (User.DoesNotExist) as e:
        return JSONResponse({'errmsg':'username or token error'})

def bind_email(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserBindEmailForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    s_name = fo_user.cleaned_data.get('username')
    s_token = fo_user.cleaned_data.get('token')
    s_email = fo_user.cleaned_data.get('email')
    try:
        mo_user = User.objects.get(name=s_name, token=s_token)
        mo_user.email = s_email
        mo_user.save()
        d_response = {'errno':0}
        return JSONResponse(d_response)
    except (User.DoesNotExist) as e:
        return JSONResponse({'errmsg':'username or token error'})

""" method template (7 lines)
def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserXXXXXForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    mo_user = User.create(fo_user.cleaned_data)
"""
