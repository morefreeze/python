from django import forms
import base64
import hashlib

class UserInfo(forms.Form):
    name = forms.CharField(required=True,max_length=255,min_length=6)
    passwd = forms.CharField(required=True,max_length=255,min_length=6)
    s_invited_username = forms.CharField(required=False,max_length=255,min_length=6)
    s_token = ''

    def gen_token(self):
        d_user_args = dict()
        d_user_args['name'] = self.name
        d_user_args['pass'] = self.passwd
        sorted(d_user_args.items(), key=lambda e:e[0])
        s_user_args = ''
        for key, value in d_user_args.items():
            s_user_args = s_user_args + "%s=%s&" %(key, value)
        s_token = hashlib.md5(base64.encodestring(s_user_args)).hexdigest().upper()
