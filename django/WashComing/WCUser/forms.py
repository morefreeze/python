from django import forms
from django.core.validators import RegexValidator

class UserRegisterForm(forms.Form):
    phone = forms.CharField(required = True,
                             min_length=11,max_length=12,
                            validators=[RegexValidator('^[0-9]+$')])
    password = forms.CharField(required = True,
                             max_length=255)
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
    password = forms.CharField(required = False,
                             max_length=255)

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
    password1 = forms.CharField(required = False, widget=forms.PasswordInput,
                             max_length=255)
    password2 = forms.CharField(required = False, widget=forms.PasswordInput,
                             max_length=255)

class UserFeedbackForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    content = forms.CharField(required = False,
                             min_length=2,max_length=255)

class UserUploadAvatarForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    avatar = forms.ImageField(required = True)

class UserBindEmailForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    email = forms.EmailField(required = True,
                            min_length=4, max_length=127)

class UserThirdBindForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    third_uid = forms.CharField(required = True,
                             max_length=63)
    access_token = forms.CharField(required = True,
                            max_length=255)
    third_tag = forms.CharField(required = True,
                             max_length=7)

class UserThirdLoginForm(forms.Form):
    third_uid = forms.CharField(required = True,
                             max_length=63)
    access_token = forms.CharField(required = True,
                            max_length=255)
    third_tag = forms.CharField(required = True,
                             max_length=7)

