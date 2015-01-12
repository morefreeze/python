from django.db import IntegrityError
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from WCLib.views import *
from WCUser.models import User
from WCCloth.serializers import ClothSerializer
from WCCloth.models import Cloth
from WCCloth.forms import ClothCategoryForm, ClothInfoForm, ClothSearchForm

# Create your views here.

@require_http_methods(['POST', 'GET'])
def category(request):
    fo_cloth = ClothCategoryForm(dict(request.GET.items() + request.POST.items()))
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
            i_gid = se_category.data['gid']
            a_clothes = Cloth.objects.filter(fa_cid=i_gid)
            se_category.data['children'] = []
            if None != a_clothes:
                for it_cloth in a_clothes:
                    se_cloth = ClothSerializer(it_cloth)
                    se_category.data['children'].append(se_cloth.data)
            d_response['data'].append(se_category.data)
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def info(request):
    fo_cloth = ClothInfoForm(dict(request.GET.items() + request.POST.items()))
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    i_cid = d_data.get('cid')
    mo_cloth = Cloth.get_cloth(i_cid)
    if None == mo_cloth:
        return JSONResponse({'errmsg':'get cloth error'})
    d_response = dict()
    d_response['title'] = mo_cloth.name
    d_response['cid'] = []
    d_response['name'] = []
    d_response['price'] = []
    if mo_cloth.is_leaf:
        d_response['cid'].append(mo_cloth.cid)
        d_response['name'].append(mo_cloth.name)
        d_response['price'].append(mo_cloth.price)
        d_response['child_num'] = 1
    else:
        a_children = Cloth.objects.filter(fa_cid=i_cid)
        for it_child in a_children:
            d_response['cid'].append(it_child.cid)
            d_response['name'].append(it_child.name)
            d_response['price'].append(it_child.price)
        d_response['child_num'] = len(a_children)
    d_response['detail'] = mo_cloth.detail
    d_response['image'] = mo_cloth.image.__str__()
    d_response['ext'] = mo_cloth.ext
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def search(request):
    fo_cloth = ClothSearchForm(dict(request.GET.items() + request.POST.items()))
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    d_data = fo_cloth.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password or permission error'})
    s_keyword = d_data.get('keyword')
    a_clothes = Cloth.objects.filter(name__contains=s_keyword, fa_cid__isnull=False)
    d_response = dict()
    d_response['data'] = []
    for it_cloth in a_clothes:
        d_response['data'].append(ClothSerializer(it_cloth).data)
    d_response['count'] = len(d_response['data'])
    d_response['errno'] = 0
    return JSONResponse(d_response)

""" method template (6 lines)
@require_http_methods(['POST', 'GET'])
def info(request):
    fo_cloth = ClothXXXXXForm(dict(request.GET.items() + request.POST.items()))
    if not fo_cloth.is_valid():
        return JSONResponse({'errmsg':fo_cloth.errors})
    mo_cloth = Cloth.create(fo_cloth.cleaned_data)
"""
