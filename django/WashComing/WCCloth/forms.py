from django import forms

class ClothCategoryForm(forms.Form):
    pass
    """
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
                             """

class ClothListForm(forms.Form):
    pass
    """
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
                             """
    gid = forms.IntegerField(required = True)

class ClothInfoForm(forms.Form):
    pass
    """
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
                             """
    cid = forms.IntegerField(required = True)

class ClothSearchForm(forms.Form):
    pass
    username = forms.CharField(required = True,
                           min_length=2,max_length=255)
    token = forms.CharField(required = True,
                             max_length=255)
    keyword = forms.CharField(required = True,
                             max_length=31)

