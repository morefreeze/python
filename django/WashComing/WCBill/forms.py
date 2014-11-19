# coding=utf-8
from django import forms

class BillSubmitForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    clothes = forms.CharField(required = True,
                             max_length=65535)
    get_time_0 = forms.DateTimeField(required = True)
    get_time_1 = forms.DateTimeField(required = True)
    return_time_0 = forms.DateTimeField(required = True)
    return_time_1 = forms.DateTimeField(required = True)
    aid = forms.IntegerField(required = True)
    comment = forms.CharField(required = False,
                              max_length=1023)
    score = forms.IntegerField(required = False)

class BillListForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
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
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    bid = forms.IntegerField(required = True)

class BillCancelForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    bid = forms.IntegerField(required = True)

class BillFeedbackForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    bid = forms.IntegerField(required = True)
    rate = forms.IntegerField(required = True)
    content = forms.CharField(required = False,
                               max_length=1023)

class BillGetFeedbackForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    bid = forms.IntegerField(required = True)

class CartSubmitForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    clothes = forms.CharField(required = True,
                             max_length=65535)

class CartListForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
