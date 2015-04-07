from django import forms
from django.core.validators import RegexValidator

class LaundryBillQueryForm(forms.Form):
    bid = forms.IntegerField(required = True)

class LaundryConfirmGetForm(forms.Form):
    bid = forms.IntegerField(required = True)
    shop_comment = forms.CharField(required = False, max_length=255)

class LaundryGetTotalPagesForm(forms.Form):
    method = forms.CharField(required = True, max_length=32)

class LaundryGetBillsForm(forms.Form):
    method = forms.CharField(required = True, max_length=32)
    page = forms.IntegerField(required = False)

class LaundryConfirmReturnForm(forms.Form):
    bid = forms.IntegerField(required = True)
    shop_comment = forms.CharField(required = False, max_length=255)

