# coding=utf-8
from django import forms

class BillSubmitForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    clothes = forms.CharField(required = True,
                             max_length=65535)
    get_time = forms.DateTimeField(required = True)
    return_time = forms.DateTimeField(required = True)
    aid = forms.IntegerField(required = True)

class BillListForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    pn = forms.IntegerField(required=False)
    deleted = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(BillListForm, self).clean()
        if not cleaned_data.get('pn'):
            cleaned_data['pn'] = 1
        if not cleaned_data.get('deleted'):
            cleaned_data['deleted'] = 0

class BillInfoForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    bid = forms.IntegerField(required = True)

class BillCancelForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    bid = forms.IntegerField(required = True)

