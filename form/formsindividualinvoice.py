from django import forms
from django.contrib.auth import get_user_model
from myapp.models import RequestResult ,OrderingTable
from betterforms.multiform import MultiModelForm # インポート

User = get_user_model()

class RequestResultForm(forms.ModelForm):
    class Meta:
        model = RequestResult
        fields = ('InvoiceNUmber',)

class OrderingTableForm(forms.ModelForm):
    class Meta:
        model = OrderingTable
        fields = ('OrderNumber', 'OrderingDate')

class IndividualMultiForm(MultiModelForm):
    form_classes = {
        "RequestResult_form": RequestResultForm, #（フォーム名：モデルフォームクラス名）
        "OrderingTable_form": OrderingTableForm,
    }

class IndividualSearchForm(forms.Form):
    query = forms.CharField(
        initial='',
        required = False, # 必須ではない
    )
    key = forms.CharField(
        initial='',
        required=False,  # 必須ではない
    )
    word = forms.CharField(
        initial='',
        required=False,  # 必須ではない
    )
    InvoiceIssueDateFrom = forms.CharField(
        initial='',
        required=False,  # 必須ではない
    )
class ChoiceForm(forms.Form):
    choice = forms.fields.ChoiceField(
        choices = (
            ('', ''),
            ('1', '発行済'),
            ('0', '未発行'),
        ),
        initial='1',
        required=False,
        widget=forms.widgets.Select
    )