from django import forms
from django.contrib.auth import get_user_model
from myapp.models import Consumetax
from django.forms import ModelChoiceField

# バリデーション
import re

User = get_user_model()

class ManagerChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.first_name + obj.last_name

class ConsumetaxForm(forms.ModelForm):
    class Meta:
        model = Consumetax
        fields = ('TaxRate', 'TaxRateDisplay', 'TaxStartDate', 'TaxEndDate', 'is_Deleted' )

class ConsumetaxSearchForm(forms.Form):
    query = forms.CharField(
        initial='',
        required = False, # 必須ではない
    )
