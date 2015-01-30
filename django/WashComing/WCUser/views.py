# coding=utf-8
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from WCLib.views import *
from WCUser.serializers import UserSerializer
from WCUser.models import User, Feedback
from WCUser.forms import UserRegisterForm, UserLoginForm, UserInfoForm, \
        UserUpdateForm, UserChangePasswordForm, UserResendActiveForm, UserActiveForm, \
        UserResendResetForm, UserResetPasswordForm, UserResetPasswordConfirmForm, \
        UserFeedbackForm, UserUploadAvatarForm, UserThirdBindForm, UserThirdLoginForm, \
        UserBindEmailForm
from WCBill.models import Coupon
import datetime as dt

# Create your views here.
@require_http_methods(['POST', 'GET'])
def register(request):
    fo_user = UserRegisterForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_phone = d_data.get('phone')
    try:
        int(s_phone)
    except (ValueError, TypeError):
        return JSONResponse({'errmsg':'phone must be number'})
    mo_user = User.create(d_data)
    s_token = User.gen_token(d_data['password'])
    mo_user.token = s_token
    s_invited_name = d_data.get('invited_username')
    if None != s_invited_name and '' != s_invited_name:
        mo_inv_user = User.query_user(s_invited_name)
        if None == mo_inv_user:
            return JSONResponse({'errmsg':"invited user[%s] not found" %(s_invited_name)})
        mo_user.invited = mo_inv_user
# user active for iOS bug
    mo_user.is_active = True
    try:
        mo_user.save()
        se_user = UserSerializer(mo_user)
# add new user coupon
        a_coupons = Coupon.objects.filter(name__contains=u'诞生礼')
        logging.debug('add coupons uid[%d] %s' %(mo_user.uid, a_coupons))
        for it_coupon in a_coupons:
            it_coupon.add_user(mo_user)
        return JSONResponse({'errno':0, 'uid':se_user.data.get('uid'), 'username':mo_user.name, 'token':s_token})
# duplicate username
    except IntegrityError as e:
        return JSONResponse({'errmsg':'username has been registered'})

@require_http_methods(['POST', 'GET'])
def login(request):
    fo_user = UserLoginForm(dict(request.GET.items() + request.POST.items()))
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

@require_http_methods(['POST', 'GET'])
def info(request):
    fo_user = UserInfoForm(dict(request.GET.items() + request.POST.items()))
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
    if '' == se_user.data['token']:
        d_response['token'] = se_user.data['third_token']
    else:
        d_response['token'] = se_user.data['token']
    d_response['avatar'] = se_user.data['avatar']
    d_response['exp'] = se_user.data['exp']
    d_response['score'] = se_user.data['score']
    d_response['level'] = User.gen_level(d_response['exp'])
    d_response['phone'] = se_user.data['phone']
    d_response['email'] = se_user.data['email']
    d_response['is_active'] = se_user.data['is_active']
    t_data = se_user.data
    d_response['third_bind'] = se_user.data['third_bind']
    d_response['errno'] = 0
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def update(request):
    fo_user = UserUpdateForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    b_modify = False
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    s_phone = d_data.get('phone')
    if None != s_phone and '' != s_phone:
        mo_user.phone = s_phone
        b_modify = True
    # if nothing to modify then do not update, or last_time will be updated
    if b_modify:
        mo_user.save()
    d_response = {'errno':0}
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def change_password(request):
    fo_user = UserChangePasswordForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    mo_user = User.vali_passwd(d_data)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    d_data['password'] = d_data['new_password']
    mo_user.token = User.gen_token(d_data['password'])
    mo_user.save()
    d_response = {'errno':0}
    d_response['username'] = mo_user.name
    d_response['token'] = mo_user.token
    return JSONResponse(d_response)

# I forget why this func here
@require_http_methods(['POST', 'GET'])
def resend_active(request):
    fo_user = UserResendActiveForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    mo_user = User.query_user(s_name)
    if None == mo_user:
        return JSONResponse({'errmsg':'active failed'})
    if mo_user.is_active:
        return JSONResponse({'errmsg':'user has been actived'})
    s_html = mo_user.send_active(request)
    try:
        send_mail(subject=u'洗来了邮箱激活', message='', from_email='', recipient_list=[s_email], \
                  fail_silently=False, html_message=s_html)
    except Exception as e:
        logging.error(e.__str__())
        return JSONResponse({'errmsg':'send mail failed, please contact admin'})
    d_response = {'errno':0}
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def active(request):
    fo_user = UserActiveForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    mo_user = User.query_user(s_name)
    if None == mo_user:
        return HttpResponse(u'激活失败，没有该用户')
    #if mo_user.is_active:
    #    return HttpResponse(u'用户已经激活')
    js_ext = mo_user.ext
    s_active_token = js_ext.get('active_token')
    if None == s_active_token or '' == s_active_token or d_data.get('active_token') != s_active_token:
        return HttpResponse(u'激活失败，也许是个无效的链接')
    tm_expire = dt.datetime.strptime(js_ext.get('active_expire'), "%Y%m%d %H:%M:%S")
    tm_now = dt.datetime.now()
    if None == tm_expire or tm_now > tm_expire:
        return HttpResponse(u'链接已经过期')
    mo_user.is_active = True
    del mo_user.ext['active_token']
    del mo_user.ext['active_expire']
    mo_user.save()
    return render_to_response('active/active_complete.html')

def reset_password(request):
    return render_to_response('reset/reset_password.html', {'form':UserResetPasswordForm})

@require_http_methods(['POST', 'GET'])
def resend_reset(request):
    fo_user = UserResendResetForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_email = d_data.get('email')
    mo_user = User.query_email(s_email)
    s_html = mo_user.send_reset(request)
    if None == mo_user:
        return HttpResponse(u'用户不存在，请检查邮箱地址')
    if not mo_user.is_active:
        return HttpResponse(u'用户未确认绑定邮箱，请先确认绑定邮箱再重置')
    try:
        send_mail(subject=u'洗来了密码重置', message='', from_email='', recipient_list=[s_email], \
                  fail_silently=False, html_message=s_html)
    except Exception as e:
        logging.error(e.__str__())
        return HttpResponse(u'邮件发送失败，请联系客服协助')
    return HttpResponse(u'重置邮件已经发出')
    #d_response = {'errno':0, 'html':s_html}
    #return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def reset_password_confirm(request):
    #if request.method != 'GET':
        #return render(request, 'reset/reset_password_confirm.html', {'validlink':0})
        #return JSONResponse({'errmsg':'method error'})
    fo_user = UserResetPasswordConfirmForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return render(request, 'reset/reset_password_confirm.html', {'validlink':0})
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    mo_user = User.query_user(s_name)
    if None == mo_user:
        return render(request, 'reset/reset_password_confirm.html', {'validlink':0})
        return JSONResponse({'errmsg':'reset password failed'})
    js_ext = mo_user.ext
    s_reset_token = js_ext.get('reset_token')
    if None == s_reset_token or '' == s_reset_token or d_data.get('reset_token') != s_reset_token:
        return render(request, 'reset/reset_password_confirm.html', {'validlink':0})
        return JSONResponse({'errmsg':'reset failed'})
    tm_expire = dt.datetime.strptime(js_ext.get('reset_expire'), "%Y%m%d %H:%M:%S")
    tm_now = dt.datetime.now()
    if None == tm_expire or tm_now > tm_expire:
        return render(request, 'reset/reset_password_confirm.html', {'validlink':0})
        return JSONResponse({'errmsg':'token expire, resend reset!'})
    s_password = d_data.get('password1')
    s_password2 = d_data.get('password2')
    if s_password != s_password2:
        return JSONResponse({'errmsg':'password does not match'})
# to set new password
    if None == s_password or '' == s_password:
        return render(request, 'reset/reset_password_confirm.html', {'validlink':1, 'form':fo_user})
    del mo_user.ext['reset_token']
    del mo_user.ext['reset_expire']
    mo_user.token = User.gen_token(s_password)
    mo_user.save()
    return render(request, 'reset/reset_password_complete.html')

def reset_password_complete(request):
    return render_to_response('reset/reset_password.html')

@require_http_methods(['POST', 'GET'])
def feedback(request):
    fo_user = UserFeedbackForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    s_content = d_data.get('content')
    mo_fb = Feedback.objects.create(own=mo_user, create_time=None, content=s_content)
    return JSONResponse({'fid': mo_fb.fid, 'errno': 0})

@require_http_methods(['POST'])
def upload_avatar(request):
    fo_user = UserUploadAvatarForm(request.POST, request.FILES)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_user.avatar = request.FILES['avatar']
    mo_user.save()
    se_user = UserSerializer(mo_user)
    return JSONResponse({'avatar': se_user.data['avatar'], 'errno': 0})

@require_http_methods(['POST', 'GET'])
def bind_email(request):
    fo_user = UserBindEmailForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token, is_active=False)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    if len(User.objects.filter(email=d_data.get('email'))) > 0:
        return JSONResponse({'errmsg':'email has been binded other user'})
    mo_user.email = d_data.get('email')
    s_html = mo_user.send_active(request)
    try:
        send_mail(subject=u'洗来了邮箱激活', message='', from_email='', recipient_list=[mo_user.email], \
                  fail_silently=False, html_message=s_html)
    except Exception as e:
        logging.error(e.__str__())
        return JSONResponse({'errmsg':'send mail failed, please contact admin'})
    d_response = {'errno':0}
    mo_user.save()
    return JSONResponse(d_response)

@require_http_methods(['POST', 'GET'])
def third_bind(request):
    fo_user = UserThirdBindForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    logging.debug(mo_user)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    s_third_uid = "%s$%s|" %(d_data.get('third_tag'), d_data.get('third_uid'))
    s_open_id = d_data.get('third_uid')
    s_access_token = d_data.get('access_token')
    s_tag = d_data.get('third_tag')
    b_valid, s_ori_third_name = User.get_third_name(s_tag, third_uid=s_open_id, access_token=s_access_token)
    if not b_valid:
        return JSONResponse({'errmsg':'this third user is not valid'})
    s_third_name = "%s$%s" %(s_tag, s_ori_third_name)
    a_user = User.objects.filter(third_uids__contains=s_third_uid, deleted=False)
    if len(a_user) > 1:
        logging.error('this account[%s,%s] has been binded multiple user' %(s_third_uid, s_access_token))
        return JSONResponse({'errmsg':'this account has been binded multiple user'})
    elif len(a_user) == 1:
        mo_third_user = a_user[0]
        if mo_third_user.uid != mo_user.uid:
# qq bind other user, or user bind other qq
            return JSONResponse({'errmsg':'this account has been binded'})
        else:
# user bind with same account, so gen third token again
            pass
    # len(a_user) == 0, third not be binded or third same
    if s_third_uid not in mo_user.third_uids \
    and ('|'+d_data.get('third_tag')+'$' in mo_user.third_uids \
    or mo_user.third_uids.startswith(d_data.get('third_tag')+'$')):
        return JSONResponse({'errmsg':'this user has been binded other third account'})
    if '' == mo_user.name:
        mo_user.name = s_third_name
    mo_user.third_uids += s_third_uid
    mo_user.third_token = User.gen_token(s_third_uid)
    mo_user.save()
    se_user = UserSerializer(mo_user)
    return JSONResponse({'errno':0, 'uid':se_user.data['uid'], 'username':s_third_uid, 'third_token':se_user.data['third_token']})

@require_http_methods(['POST', 'GET'])
def third_login(request):
    fo_user = UserThirdLoginForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_third_uid = "%s$%s|" %(d_data.get('third_tag'), d_data.get('third_uid'))
    s_open_id = d_data.get('third_uid')
    s_access_token = d_data.get('access_token')
    s_tag = d_data.get('third_tag')
    b_valid, s_ori_third_name = User.get_third_name(s_tag, third_uid=s_open_id,  access_token=s_access_token)
    if not b_valid:
        return JSONResponse({'errmsg':'this third user is not valid'})
    s_third_name = "%s$%s" %(s_tag, s_ori_third_name)
    a_user = User.objects.filter(third_uids__contains=s_third_uid, deleted=False)
    if len(a_user) > 1:
        logging.error('this account[%s,%s] has been binded multiple user' %(s_third_uid, s_access_token))
        return JSONResponse({'errmsg':'this account has been binded multiple user'})
    elif len(a_user) == 1:
        mo_user = a_user[0]
    else:
        mo_user = User.objects.create(name=s_third_uid)
        mo_user.third_uids += s_third_uid
    mo_user.third_token = User.gen_token(s_third_uid)
# this is pure third user instead of binded
    if '' == mo_user.token or s_third_name == mo_user.name:
        mo_user.token = mo_user.third_token
    mo_user.save()
    se_user = UserSerializer(mo_user)
    return JSONResponse({'errno':0, 'uid':se_user.data['uid'], 'username':s_third_uid, 'third_token':se_user.data['third_token']})

"""
def admin_upload_avatar(request):
    if request.method != 'POST':
        form = UserUploadAvatarForm()
        mos = User.objects.exclude(avatar__exact='')
        return render_to_response('list.html',
                                  {'documents':mos,'form':form},
                                 context_instance=RequestContext(request))
        #return JSONResponse({'errmsg':'method error'})
    fo_user = UserUploadAvatarForm(request.POST, request.FILES)
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
    mo_user.avatar = request.FILES['avatar']
    mo_user.save()
    return HttpResponseRedirect(reverse('WCUser.views.admin_upload_avatar'))
"""

""" method template (11 lines)
@require_http_methods(['POST', 'GET'])
def info(request):
    fo_user = UserXXXXXForm(dict(request.GET.items() + request.POST.items()))
    if not fo_user.is_valid():
        return JSONResponse({'errmsg':fo_user.errors})
    d_data = fo_user.cleaned_data
    s_name = d_data.get('username')
    s_token = d_data.get('token')
    mo_user = User.get_user(s_name, s_token)
    if None == mo_user:
        return JSONResponse({'errmsg':'username or password error'})
"""
