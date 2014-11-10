from django import forms

class UserRegisterForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    password = forms.CharField(required = True,
                             max_length=255)
    phone = forms.CharField(required = True,
                             min_length=11,max_length=12)

class UserLoginForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    password = forms.CharField(required = True,
                             max_length=255)

class UserInfoForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)

class UserBindEmailForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    email = forms.CharField(required = True,
                           min_length=3,max_length=128)

class UserUpdateForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    password = forms.CharField(required = True,
                             max_length=255)


