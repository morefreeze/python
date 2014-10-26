from django import forms

class ClothCategoryForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)

class ClothListForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    password = forms.CharField(required = True,
                             max_length=255)
    gid = forms.IntegerField(required = True)

class ClothInfoForm(forms.Form):
    username = forms.CharField(required = True,
                           min_length=3,max_length=255)
    token = forms.CharField(required = True,
                             max_length=32)
    cid = forms.IntegerField(required = True)

