from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import CustomerSupplier
# LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 得意先月次集計表
class CustomerMonthlyListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    template_name = "crud/monthlyaggregation/CustomerMonthlyaggregationlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #2025-05-20 追加
        context.update(CustomerCode_From = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_To = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_Max = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').reverse().filter(is_Deleted=0).first())
    
        return context
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset
