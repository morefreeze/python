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
    phone = forms.CharField(required = False,
                             min_length=11,max_length=12)

class UserChangePasswordForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    password = forms.CharField(required = True,
                             max_length=255)
    new_password = forms.CharField(required = True,
                             max_length=255)

class UserResendActiveForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)

class UserActiveForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    active_token = forms.CharField(required = True,
                             max_length=32)

class UserResetPasswordForm(forms.Form):
    email = forms.CharField(required = True,
                           min_length=2,max_length=255)

class UserResendResetForm(forms.Form):
    email = forms.CharField(required = True,
                           min_length=2,max_length=255)

class UserResetPasswordConfirmForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255, widget=forms.HiddenInput())
    reset_token = forms.CharField(required = True,
                             max_length=32, widget=forms.HiddenInput())
    password1 = forms.CharField(required = False,
                             max_length=255)
    password2 = forms.CharField(required = False,
                             max_length=255)

