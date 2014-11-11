from django.db import IntegrityError
from django.shortcuts import render
from WCLib.views import *
from WCUser.serializers import UserSerializer
from WCUser.models import User
from WCUser.forms import UserRegisterForm, UserLoginForm, UserInfoForm, \
        UserBindEmailForm, UserUpdateForm

# Create your views here.

def register(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserRegisterForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    mo_user = User.create(fo_user.cleaned_data)
    d_data = fo_user.cleaned_data
    s_token = User.gen_token(d_data)
    s_phone = d_data.get('phone')
    try:
        int(s_phone)
    except (ValueError, TypeError):
        return JSONResponse({'errmsg':'phone must be number'})
    mo_user.token = s_token
    mo_user.phone = s_phone
    s_invited_name = d_data.get('invited_username')
    if None != s_invited_name and '' != s_invited_name:
        mo_inv_user = User.query_user(s_invited_name)
        if None == mo_inv_user:
            return JSONResponse({'errmsg':"invited user[%s] not found" %(s_invited_name)})
        mo_user.invited = mo_inv_user
    try:
        mo_user.save()
        se_user = UserSerializer(mo_user)
        return JSONResponse({'errno':0, 'uid':se_user.data.get('uid'), 'token':s_token})
# duplicate username
    except IntegrityError as e:
        return JSONResponse({'errmsg':'username has been registered'})

def login(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserLoginForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    mo_user = User.vali_passwd(d_data)
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
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    se_user = UserSerializer(mo_user)
    d_response = dict()
    d_response['uid'] = se_user.data['uid']
    d_response['username'] = se_user.data['name']
    d_response['token'] = se_user.data['token']
    d_response['exp'] = se_user.data['exp']
    d_response['score'] = se_user.data['score']
    d_response['level'] = User.gen_level(d_response['score'])
    d_response['email'] = se_user.data['email']
    d_response['errno'] = 0
    return JSONResponse(d_response)

def bind_email(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserBindEmailForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    if '' != mo_user.email:
        return JSONResponse({'errmsg':'user has email, can not bind again'})
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    s_email = d_data.get('email')
    mo_user = User.objects.get(name=s_name, token=s_token)
    mo_user.email = s_email
    mo_user.save()
    d_response = {'errno':0}
    return JSONResponse(d_response)

def update(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserUpdateForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    if None != d_data.get('password') and '' != d_data.get('password'):
        mo_user.token = User.gen_token(d_data)
    s_phone = d_data.get('phone')
    if None != s_phone and '' != s_phone:
        mo_user.phone = s_phone
    mo_user.save()
    d_response = {'errno':0}
    d_response['username'] = mo_user.name
    d_response['token'] = mo_user.token
    return JSONResponse(d_response)

""" method template (12 lines)
def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_user = UserXXXXXForm(request.GET)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
"""
