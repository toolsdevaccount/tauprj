from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import CustomerSupplier
from django.contrib.auth import get_user_model
# LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 担当者別売上一覧表
class SalesPersonListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    template_name = "crud/salesperson/salespersonlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(Manager_From = get_user_model().objects.values('id','first_name', 'last_name'))
        context.update(Manager_To = get_user_model().objects.values('id','first_name', 'last_name'))
    
        return context
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset
