from django.shortcuts import render
from django.views.generic import ListView 
from myapp.models import CustomerSupplier,OrderingDetail, RequestResult
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.form.formshistory import historyManageForm

# models
from django.db.models import Q
# ajax
from django.http import JsonResponse

#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class HistoryManageView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    form_class =  historyManageForm
    template_name = "crud/history/list/historylist.html"

    def get_context_data(self, **kwargs):
        context = super(HistoryManageView, self).get_context_data(**kwargs)

        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset

    def List(request, OrderNumber1, OrderNumber2, OrderNumber3):
        if OrderNumber1!='0':
            Condition_OrderNumber1 = Q(OrderingTableId__OrderNumber=OrderNumber1)
        else:
            Condition_OrderNumber1 = Q()
        #出荷先
        if OrderNumber2!='0':
            Condition_OrderNumber2 = Q(OrderingTableId__OrderNumber=OrderNumber2)
        else:
            Condition_OrderNumber2 = Q()
        #依頼先
        if OrderNumber3!='0':
            Condition_OrderNumber3 = Q(OrderingTableId__OrderNumber=OrderNumber3)
        else:
            Condition_OrderNumber3 = Q()

        queryset =  OrderingDetail.objects.values(
            'id',
            'OrderingTableId__id',
            'OrderingTableId__SlipDiv',
            'OrderingTableId__OrderNumber',
            'DetailItemNumber',
            'OrderingTableId__ProductName',
            'OrderingTableId__OrderingCount',
            'OrderingTableId__DestinationCode_id__CustomerCode',
            'OrderingTableId__DestinationCode_id__CustomerName',
            'OrderingTableId__ShippingCode_id__CustomerCode',
            'OrderingTableId__ShippingCode_id__CustomerName',
            'OrderingTableId__RequestCode_id__CustomerCode',
            'OrderingTableId__RequestCode_id__CustomerName',
            ).filter(Q(Condition_OrderNumber1) | Q(Condition_OrderNumber2) |Q(Condition_OrderNumber3) , is_Deleted=0
                    ).order_by(
                        'OrderingTableId__SlipDiv',
                        'OrderingTableId__OrderNumber',
                    )

        context = {
            'form': queryset,
        }

        return render(request, 'crud/history/list/historylist.html', context)
    
    def history_result_ajax(request):
        if request.method == 'GET':  # GETの処理
            table_param = request.GET.get("tableid")  # GETパラメータ
            detail_param = request.GET.get("detailid")  # GETパラメータ
            #
            detail = list(RequestResult.objects.values(
                'id',
                'OrderingId__id',
                'OrderingDetailId__id',
                'OrderingId__OrderingDate',
                'OrderingDetailId__DetailItemNumber',
                'OrderingDetailId__DetailColorNumber',
                'OrderingDetailId__DetailColor',
                'OrderingDetailId__DetailTailoring',
                'OrderingDetailId__DetailVolume',
                'OrderingDetailId__DetailUnitPrice',
                'OrderingDetailId__DetailPrice',
                'OrderingDetailId__DetailOverPrice',
                'OrderingDetailId__DetailSellPrice',
                'ResultDate',
                'ResultItemNumber',
                'ShippingDate',
                'ShippingVolume',
                'SlipNumber',
                'OrderingId__DestinationCode_id__CustomerCode',
                'OrderingId__DestinationCode_id__CustomerName',
                'OrderingId__SupplierCode_id__CustomerCode',
                'OrderingId__SupplierCode_id__CustomerName',
                'OrderingId__ShippingCode_id__CustomerCode',
                'OrderingId__ShippingCode_id__CustomerName',
                'OrderingId__CustomeCode_id__CustomerCode',
                'OrderingId__CustomeCode_id__CustomerName',
                'OrderingId__RequestCode_id__CustomerCode',
                'OrderingId__RequestCode_id__CustomerName',
                'OrderingId__RequestCode_id__ManagerCode',
                'OrderingId__RequestCode_id__ManagerCode__first_name',
                'OrderingId__RequestCode_id__ManagerCode__last_name',
                ).filter(OrderingId_id=table_param,OrderingDetailId_id=detail_param,is_Deleted=0))
        
            context = {
                'list': detail,
            }

            return JsonResponse(context)
