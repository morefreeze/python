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
    a_category = Cloth.get_category()
    d_response = dict()
    d_response['data'] = []
    if None != a_category:
        for it_category in a_category:
            se_category = ClothSerializer(it_category)
# replace cid to gid
            se_category.data['gid'] = se_category.data['cid']
            del se_category.data['cid']
            d_response['data'].append(se_category.data)
    d_response['errno'] = 0
    return JSONResponse(d_response)

def list(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_cloth = ClothListForm(request.GET)
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    i_gid = d_data.get('gid')
    a_cloth = Cloth.objects.filter(fa_cid=i_gid, is_leaf=True, deleted=False)
    d_response = dict()
    d_response['data'] = []
    if None != a_cloth:
        for it_cloth in a_cloth:
            se_cloth = ClothSerializer(it_cloth)
            d_response['data'].append(se_cloth.data)
    d_response['count'] = len(d_response['data'])
    d_response['errno'] = 0
    return JSONResponse(d_response)

def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_cloth = ClothInfoForm(request.GET)
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    i_cid = d_data.get('cid')
    mo_cloth = Cloth.get_cloth(i_cid)
    if None == mo_cloth:
        return JSONResponse({'errmsg':'get cloth error'})
    se_cloth = ClothSerializer(mo_cloth)
    d_response = dict()
    d_response['cid'] = se_cloth.data['cid']
    d_response['name'] = se_cloth.data['name']
    d_response['detail'] = se_cloth.data['detail']
    d_response['price'] = se_cloth.data['price']
    d_response['errno'] = 0
    return JSONResponse(d_response)

""" method template (7 lines)
def info(request):
    if request.method != 'GET':
        return JSONResponse({'errmsg':'method error'})
    fo_cloth = ClothXXXXXForm(request.GET)
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    mo_cloth = Cloth.create(fo_cloth.cleaned_data)
"""
