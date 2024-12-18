from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import RequestResult, CustomerSupplier
from myapp.form.formsinvoice import InvoiceMultiForm,InvoiceSearchForm,ClosingChoiceForm
# メッセージ
from django.contrib import messages
# 検索機能のために追加
# 計算用
from django.db.models import Sum, F, Q, IntegerField
from django.db.models.functions import Coalesce
# LOG出力設定
import logging
logger = logging.getLogger(__name__)
#Pagenation
from django.core.paginator import Page
#pandas
import pandas as pd

# 請求情報一覧/検索
class invoiceListView(LoginRequiredMixin,ListView):
    model = RequestResult
    form_class = InvoiceMultiForm
    paginate_by = 20
    template_name = "crud/invoice/invoicelist.html"
    queryset = RequestResult.objects.order_by('InvoiceNUmber')

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
            self.request.POST.get('key', None),
            self.request.POST.get('word', None),
            self.request.POST.get('InvoiceIssueDateFrom', None),
        ]

        if 'clear' in request.POST:
            del request.session['invsearch']
        else:
            request.session['invsearch'] = search

        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'invsearch' in self.request.session:
            search = self.request.session['invsearch']
            query = search[0]
            key = search[1]
            word = search[2]
            InvoiceIssueDateFrom = search[3]
        else:
            query = self.request.POST.get('query', None)
            key = self.request.POST.get('key', None)
            word = self.request.POST.get('word', None)
            InvoiceIssueDateFrom = self.request.POST.get('InvoiceIssueDateFrom', None)

        queryset =  RequestResult.objects.values(
            'id',
            'InvoiceNUmber',
            'OrderingId__CustomeCode',
            'OrderingId__SlipDiv',
            'OrderingId__OrderNumber',
            'OrderingId__CustomeCode_id__CustomerName',
            'OrderingId__ProductName',
            'OrderingId__OrderingCount',
            'ShippingDate',
            'ResultDate',
            'InvoiceIssueDate',
            ).annotate(
                Abs_total=Coalesce(F('ShippingVolume') * F('OrderingDetailId__DetailSellPrice'),0,output_field=IntegerField()),
                Shipping_total=Sum('ShippingVolume')
                )
        # 個別請求書番号が付加されたものかつ発行済
        queryset = queryset.filter(Q(InvoiceNUmber__gt=0), Q(InvoiceIssueDiv=1), is_Deleted=0,OrderingDetailId__DetailSellPrice__gt=0,)
        # 個別請求書番号降順
        queryset = queryset.order_by('InvoiceNUmber').reverse()
        # 検索
        if query:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=query) | Q(OrderingId__CustomeCode__CustomerName__icontains=query) | Q(OrderingId__OrderNumber__icontains=query) |
                 Q(OrderingId__ProductName__icontains=query) | Q(OrderingId__OrderingCount__icontains=query)
            )

        if key:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=key) | Q(OrderingId__CustomeCode__CustomerName__icontains=key) | Q(OrderingId__OrderNumber__icontains=key) |
                 Q(OrderingId__ProductName__icontains=key) | Q(OrderingId__OrderingCount__icontains=key)
            )

        if word:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=word) | Q(OrderingId__CustomeCode__CustomerName__icontains=word) | Q(OrderingId__OrderNumber__icontains=word) |
                 Q(OrderingId__ProductName__icontains=word) | Q(OrderingId__OrderingCount__icontains=word)
            )

        if InvoiceIssueDateFrom:
            queryset = queryset.filter(Q(InvoiceIssueDate__gte=(InvoiceIssueDateFrom)))

        #queryset Dataframeに変換-------------------------------------------------#
        df = pd.DataFrame(queryset, columns=[
            'id',
            'InvoiceNUmber',
            'OrderingId__CustomeCode',
            'OrderingId__SlipDiv',
            'OrderingId__OrderNumber',
            'OrderingId__CustomeCode_id__CustomerName',
            'OrderingId__ProductName',
            'OrderingId__OrderingCount',
            'ShippingDate',
            'ResultDate',
            'InvoiceIssueDate',
            'Abs_total',
            'Shipping_total',
            ])
        #Dataframeで集計-------------------------------------------------------#
        sales_sum = df[[
            'InvoiceNUmber',
            'Abs_total',
            'Shipping_total'
            ]].groupby([
                'InvoiceNUmber',
                ], as_index =False).sum()
        _tuple =  [tuple(x) for x in sales_sum.values]
        #個別請求書番号別合計計算------------------------------------------------#
        InvoiceData=[]
        InvoiceNumber=0
        for d in queryset:
            SellTotal = 0
            ShippingTotal=0
            if d['InvoiceNUmber']!=InvoiceNumber:
                InvoiceData.append(d)
            InvoiceNumber=d['InvoiceNUmber']
            for q in _tuple:
                if q[0]==InvoiceNumber:
                    SellTotal+=int(q[1])
                    ShippingTotal+= (q[2])
                    d['Abs_total'] = SellTotal
                    d['Shipping_total']=ShippingTotal
        #--------------------------------------------------------------------#
        return InvoiceData

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        key = ''
        word = ''
        InvoiceIssueDateFrom = ''

        if 'invsearch' in self.request.session:
            search = self.request.session['invsearch']
            query = search[0]
            key = search[1]
            word = search[2]
            InvoiceIssueDateFrom = search[3]

        default_data = {'query': query,
                'key': key,
                'word': word,
                'InvoiceIssueDateFrom': InvoiceIssueDateFrom,
                }
        form = InvoiceSearchForm(initial=default_data) # 検索フォーム
        context['invsearch'] = form
        context.update(InvoiceCustomerCode_From = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(InvoiceCustomerCode_To = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(InvoiceCustomerCode_Max = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').reverse().filter(is_Deleted=0).first())
        context.update(Closing = ClosingChoiceForm())
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)   
        return context