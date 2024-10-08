from django import forms
from django.contrib.auth import get_user_model
from myapp.models import Merchandise, MerchandiseDetail, MerchandiseColor, MerchandiseSize, MerchandiseFileUpload
from django.forms import ModelChoiceField

# バリデーション
import re

User = get_user_model()

class ManagerChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.first_name + obj.last_name

class MerchandiseForm(forms.ModelForm):
    McdManagerCode = ManagerChoiceField(queryset=get_user_model().objects.all(),empty_label='')

    class Meta:
        model = Merchandise
        fields = ('McdTreatmentCode', 'McdPartNumber', 'McdManagerCode', 'McdUnitPrice', 'McdUnitCode', 
                  'McdSellPrice', 'McdProcessfee', 'McdProcessCode', 'McdTempPartNumber'
                  )
  
MerchandiseFormset = forms.inlineformset_factory(
    Merchandise, MerchandiseDetail, 
    fields=('McdDtProductName','McdDtOrderingCount','McdDtStainMixRatio','McdDtlPrice','McdDtUnitCode','is_Deleted'),
    extra=0,min_num=1,validate_min=True,can_delete=True
)

MerchandiseColorFormset = forms.inlineformset_factory(
    Merchandise, MerchandiseColor, 
    fields=('McdColor','McdColorNumber','is_Deleted'),
    extra=0,min_num=1,validate_min=True,can_delete=True
)

MerchandiseSizeFormset = forms.inlineformset_factory(
    Merchandise, MerchandiseSize, 
    fields=('McdSize','is_Deleted'),
    extra=0,min_num=1,validate_min=True,can_delete=True
)

MerchandisefileFormset = forms.inlineformset_factory(
    Merchandise, MerchandiseFileUpload, 
    fields=('uploadPath','is_Deleted'),
    extra=0,min_num=1,max_num=3,validate_min=True,can_delete=True
)

class SearchForm(forms.Form):
    query = forms.CharField(
        initial='',
        required = False, # 必須ではない
    )
