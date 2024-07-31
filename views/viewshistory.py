from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from myapp.models import OrderingTable, OrderingDetail, RequestResult
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, CharField
from myapp.form.formsrequestresult import RequestResultForm, HistorySearchForm
# 検索機能のために追加
from django.db.models import Q
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class HistoryListView(LoginRequiredMixin,ListView):
    model = OrderingTable
    form_class = RequestResultForm
    context_object_name = 'object_list'
    queryset = OrderingTable.objects.select_related()
    template_name = "crud/history/list/historylist.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
            self.request.POST.get('key', None),
            self.request.POST.get('word', None),
            self.request.POST.get('historydateFrom', None),
            self.request.POST.get('historydateTo', None),
        ]
        if 'clear' in request.POST:
            del request.session['historysearch']
        else:
            request.session['historysearch'] = search
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'historysearch' in self.request.session:
            search = self.request.session['historysearch']
            query = search[0]
            key = search[1]
            word = search[2]
            historydateFrom = search[3]
            historydateTo = search[4]
        else:
            query = self.request.POST.get('query', None)
            key = self.request.POST.get('key', None)
            word = self.request.POST.get('word', None)
            historydateFrom = self.request.POST.get('historydateFrom', None)
            historydateTo = self.request.POST.get('historydateTo', None)

        # 依頼日、伝票区分、オーダーNO大きい順で抽出
        queryset = OrderingTable.objects.order_by('OrderingDate','SlipDiv','OrderNumber').reverse()
        # 削除済以外、管理者の場合は全レコード表示（削除済以外）
        if self.request.user.is_superuser == 0:
            #queryset = queryset.filter(is_Deleted=0,Created_id=self.request.user.id)
            # 全ユーザ表示
            queryset = queryset.filter(is_Deleted=0)
        else:
            queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                Q(SampleDiv__divname__icontains=query) | Q(OutputDiv__outputdivname__icontains=query) | Q(ManagerCode__first_name__icontains=query) |
                Q(ProductName__icontains=query) | Q(DestinationCode__CustomerOmitName__icontains=query) | Q(SupplierCode__CustomerOmitName__icontains=query) |
                Q(ShippingCode__CustomerOmitName__icontains=query) | Q(CustomeCode__CustomerOmitName__icontains=query) | Q(RequestCode__CustomerOmitName__icontains=query) |
                Q(SlipDiv__contains=query) | Q(OrderNumber__icontains=query)
            )
        if key:
            queryset = queryset.filter(
                Q(SampleDiv__divname__icontains=key) | Q(OutputDiv__outputdivname__icontains=key) | Q(ManagerCode__first_name__icontains=key) |
                Q(ProductName__icontains=key) | Q(DestinationCode__CustomerOmitName__icontains=key) | Q(SupplierCode__CustomerOmitName__icontains=key) |
                Q(ShippingCode__CustomerOmitName__icontains=key) | Q(CustomeCode__CustomerOmitName__icontains=key) | Q(RequestCode__CustomerOmitName__icontains=key) |
                Q(SlipDiv__contains=key) | Q(OrderNumber__icontains=key) 
            )

        if word:
            queryset = queryset.filter(
                Q(SampleDiv__divname__icontains=word) | Q(OutputDiv__outputdivname__icontains=word) | Q(ManagerCode__first_name__icontains=word) |
                Q(ProductName__icontains=word) | Q(DestinationCode__CustomerOmitName__icontains=word) | Q(SupplierCode__CustomerOmitName__icontains=word) |
                Q(ShippingCode__CustomerOmitName__icontains=word) | Q(CustomeCode__CustomerOmitName__icontains=word) | Q(RequestCode__CustomerOmitName__icontains=word) | 
                Q(SlipDiv__contains=word) | Q(OrderNumber__icontains=word) 
            )

        if historydateFrom and historydateTo:
            queryset = queryset.filter(Q(OrderingDate__range=(historydateFrom,historydateTo)))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        key = ''
        word = ''
        historydateFrom = ''
        historydateTo = ''
        if 'historysearch' in self.request.session:
            search = self.request.session['historysearch']
            query = search[0]
            key = search[1]
            word = search[2]
            historydateFrom = search[3]
            historydateTo = search[4]

        default_data = {'query': query,
                        'key': key,
                        'word': word,
                        'historydateFrom': historydateFrom,
                        'historydateTo': historydateTo,
                       }
        
        form = HistorySearchForm(initial=default_data) # 検索フォーム
        context['historysearch'] = form
        return context

# 受発注情報編集
class HistoryDetailView(LoginRequiredMixin,TemplateView):
    model = RequestResult
    template_name = "crud/history/update/historyform.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        queryset = RequestResult.objects.filter(is_Deleted=0, OrderingId_id=pk)       
        key = queryset.values_list("OrderingDetailId_id",flat=True).first()

        querysetdetail = OrderingDetail.objects.values(
            'id',
            'DetailItemNumber',
            'DetailColorNumber',
            'DetailColor',
            'DetailTailoring',
            'DetailVolume',
            'DetailUnitPrice',
            'DetailPrice',
            'DetailOverPrice',
            'DetailSellPrice',
        ).filter(
            is_Deleted=0,
            OrderingTableId=pk
        ).annotate(
             DetailUnitDiv=Case( 
                When(DetailUnitDiv=0, then=Value('')),
                When(DetailUnitDiv=1, then=Value('Kg')),
                When(DetailUnitDiv=2, then=Value('本')),
             default=Value(''), 
             output_field=CharField()) 
        )

        querysetresult = RequestResult.objects.values(
            'id',
            'ResultDate',
            'ResultItemNumber',
            'ShippingDate',
            'ShippingVolume',
            'SlipNumber',
        ).filter(
            is_Deleted=0,
            OrderingId=pk
        )

        context = {
            'formset': querysetdetail,
            'inlinesRecord': querysetresult,
        }

        return context