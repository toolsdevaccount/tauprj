from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import CustomerSupplier
# LOG出力設定
import logging
logger = logging.getLogger(__name__)
# 日時
from django.utils import timezone
from dateutil import relativedelta

# 仕入台帳
class PurchaseLedgerListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    template_name = "crud/Ledger/purchaseledgerlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(CustomerCode_From = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_To = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_Max = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').reverse().filter(is_Deleted=0).first())
        context.update(GetMonth=timezone.now().date() + relativedelta.relativedelta(months=-1))
    
        return context
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset
