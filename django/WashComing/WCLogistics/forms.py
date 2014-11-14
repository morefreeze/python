from django import forms

class AddressAddForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    real_name = forms.CharField(required = True,
                             min_length=3,max_length=255)
    provice = forms.CharField(required = True,
                             min_length=2,max_length=15)
    city = forms.CharField(required = True,
                             min_length=2,max_length=63)
    area = forms.CharField(required = True,
                             min_length=2,max_length=15)
    phone = forms.CharField(required = True,
                             min_length=7,max_length=12)
    address = forms.CharField(required = True,
                             min_length=3,max_length=255)
    set_default = forms.BooleanField(required = False)

class AddressUpdateForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    aid = forms.IntegerField(required = True)
    real_name = forms.CharField(required = False,
                             min_length=3,max_length=255)
    provice = forms.CharField(required = False,
                             min_length=2,max_length=16)
    city = forms.CharField(required = False,
                             min_length=2,max_length=63)
    area = forms.CharField(required = True,
                             min_length=2,max_length=15)
    address = forms.CharField(required = False,
                             min_length=3,max_length=255)

class AddressDeleteForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    aid = forms.IntegerField(required = True)

class AddressListForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)

class AddressSetDefaultForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    aid = forms.IntegerField(required = True)

class AddressInfoForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    aid = forms.IntegerField(required = True)

