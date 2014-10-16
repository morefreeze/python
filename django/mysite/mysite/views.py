from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, render_to_response
from mysite.forms import EncodeForm
from mysite.user_info import UserInfo
from subprocess import check_output, STDOUT, CalledProcessError
import os
import json

def fake_ssh(request):
    valid_cmd = ['ls', 'php', 'cat', 'grep', 'ps', 'python']
    DEBUG = 1
    sec_arr = ['123456789',
               'morefreeze']
    sec = request.GET.get('secret', '').encode('utf-8')
    ret = dict()
    while sec == sec_arr[DEBUG]:
        cmd = request.GET.get('cmd', '').encode('utf-8')
        if '' == cmd:
            ret['err'] = 'cmd is empty'
            break
        cmd_arr = cmd.split('|')
        valid_flag = 1
        for t_cmd in cmd_arr:
            t_cmd = t_cmd.strip()
            t_cmd = t_cmd.split(' ', 1)[0]
            t_cmd = t_cmd.strip()
            t_cmd = os.path.basename(t_cmd)
            if not t_cmd in valid_cmd:
                valid_flag = 0
                break
        if not valid_flag:
            ret['err'] = 'cmd is not valid'
            break
        try:
            ret['output'] = check_output(cmd, shell=True, stderr=STDOUT)
            # keep this as same as CalledProcessError
            ret['returncode'] = 0
            ret['cmd'] = cmd
        except CalledProcessError as e:
            ret['returncode'] = e.returncode
            ret['output'] = e.output
            ret['cmd'] = e.cmd
        break
    return HttpResponse(json.dumps(ret, ensure_ascii=False))

def encode_qid(request):
    if request.method == 'POST':
        form = EncodeForm(request.POST)
    else:
        form = EncodeForm()
    return render_to_response('encode_form.html', {'form': form})

def register(request):
    if request.method == 'GET':
        user_info = UserInfo(request.GET)
        if user_info.is_valid():
            user_info.gen_token()
            ret = {'token':user_info.s_token}
        else:
            ret = {'errmsg':'%s %s' %(user_info.s_token, user_info.s_token)}
    else:
        ret = {'errmsg':'only for GET'}

    return JsonResponse(ret)
