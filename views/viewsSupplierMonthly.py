from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import CustomerSupplier
# LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 得意先月次集計表
class SupplierMonthlyListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    template_name = "crud/monthlyaggregation/SupplierMonthlyaggregationlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        return context
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset
