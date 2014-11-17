from django import forms

class UserRegisterForm(forms.Form):
    email = forms.CharField(required = True,
                           min_length=3,max_length=128)
    password = forms.CharField(required = True,
                             max_length=255)
    phone = forms.CharField(required = True,
                             min_length=11,max_length=12)
    invited_username = forms.CharField(required = False,
                           min_length=2,max_length=255)

class UserLoginForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    password = forms.CharField(required = True,
                             max_length=255)

class UserInfoForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)

class UserUpdateForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    password = forms.CharField(required = False,
                             max_length=255)
    phone = forms.CharField(required = False,
                             min_length=11,max_length=12)

class UserResendActiveForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)

class UserActiveForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    active_token = forms.CharField(required = True,
                             max_length=32)

