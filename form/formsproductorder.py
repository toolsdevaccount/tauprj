from django import forms
from django.contrib.auth import get_user_model
#from django.contrib.auth.forms import UserCreationForm
from myapp.models import ProductOrder, ProductOrderDetail, CustomerSupplier, Merchandise

from django.forms import ModelChoiceField
from datetime import datetime

# バリデーション
import re

User = get_user_model()

class ManagerChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.first_name + obj.last_name

class CustomerSupplierChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return  obj.CustomerCode + ":" + obj.CustomerOmitName[0:5]

class ProductOrderForm(forms.ModelForm):
    ProductOrderManagerCode = ManagerChoiceField(queryset=get_user_model().objects.all(),empty_label='')

    class Meta:
        model = ProductOrder
        fields = ('ProductOrderMerchandiseCode', 'ProductOrderOrderingDate', 'ProductOrderManagerCode','ProductOrderSlipDiv', 'ProductOrderOrderNumber',
                  'ProductOrderPartNumber','ProductOrderApparelCode','ProductOrderDestinationCode','ProductOrderSupplierCode','ProductOrderShippingCode',
                  'ProductOrderCustomeCode','ProductOrderRequestCode','ProductOrderDeliveryDate','ProductOrderBrandName','ProductOrderSupplierPerson',
                  'ProductOrderTitleDiv','ProductOrderMarkName','ProductOrderSummary','is_Ordered'
                  )   

    # 商品コード存在チェック
    def clean_ProductOrderMerchandiseCode(self):
        McdPartNumber = self.cleaned_data['ProductOrderMerchandiseCode']
        idcnt = Merchandise.objects.filter(id = McdPartNumber).count()
        if idcnt == 0:
            raise forms.ValidationError(u'商品コードが存在しません')
        return McdPartNumber

    # オーダーナンバー重複チェック
    #def clean_ProductOrderOrderNumber(self):
    #    ProductOrderOrderNumber = self.cleaned_data['ProductOrderOrderNumber']
    #    idcnt = ProductOrder.objects.filter(id__exact = self.instance.pk).count()
    #    OrderNumbercnt = ProductOrder.objects.filter( ProductOrderOrderNumber__exact = ProductOrderOrderNumber.zfill(7)).count()
    #    if idcnt > 0:
    #        OrderNumbercnt = 0           
    #    if ProductOrderOrderNumber:
    #        if OrderNumbercnt > 0:
    #            raise forms.ValidationError(u'オーダーNOが重複しています')
    #    return ProductOrderOrderNumber

ProductOrderFormset = forms.inlineformset_factory(
    ProductOrder, ProductOrderDetail, 
    fields=('PodColorId','PodSizeId','PodVolume','is_Deleted'),
    extra=0,min_num=1,max_num=10,validate_min=True,can_delete=True
)


   
#OrderingFormset = forms.inlineformset_factory(
    #OrderingTable, OrderingDetail, 
    #fields=('DetailItemNumber','DetailColorNumber','DetailColor','DetailTailoring','DetailVolume','DetailUnitPrice',
    #        'DetailSellPrice','DetailPrice','DetailOverPrice','DetailSummary','SpecifyDeliveryDate','StainAnswerDeadline','DeliveryManageDiv','is_Deleted',
    #        ),
    #extra=0,min_num=1,validate_min=True,can_delete=True
#)

    # 発注日
    #def clean_ProductOrderOrderingDate(self):
    #    ProductOrderOrderingDate = self.cleaned_data['ProductOrderOrderingDate']
    #    if ProductOrderOrderingDate:
    #        try:
    #            if not re.match(r'/^[0-9]{4}/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$/', ProductOrderOrderingDate):
    #                raise forms.ValidationError(u'yyyy-mm-dd形式で')
    #        except Exception:
    #            raise forms.ValidationError(u'日付に変換できません')
    #    return ProductOrderOrderingDate

class SearchForm(forms.Form):
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
    productorderdateFrom = forms.CharField(
        initial='',
        required=False,  # 必須ではない
    )
    productorderdateTo = forms.CharField(
        initial='',
        required=False,  # 必須ではない
    )