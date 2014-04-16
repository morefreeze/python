from django import forms

class EncodeForm(forms.Form):
    help_txt = forms.Field()
    help_txt.help_text = 'input qid list, like http://zhidao.baidu.com/question/123 or 123'
    qid_list = forms.CharField(widget=forms.Textarea)
    result_txt = forms.CharField(widget=forms.Textarea)
