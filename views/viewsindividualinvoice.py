from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.models import RequestResult
from myapp.form.formsindividualinvoice import IndividualMultiForm,IndividualSearchForm
# 検索機能のために追加
from django.db.models import Q
# メッセージ
from django.contrib import messages
# LOG出力設定
import logging
logger = logging.getLogger(__name__)
# 日時
import datetime
from dateutil import relativedelta
#Pagenation
from django.core.paginator import Page

# 個別請求情報一覧/検索
class individualinvoiceListView(LoginRequiredMixin,ListView):
    model = RequestResult
    form_class = IndividualMultiForm
    paginate_by = 20
    template_name = "crud/individualinvoice/individualinvoice.html"
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

        #前月月初取得
        dt_now = datetime.datetime.now().date()
        startdate = dt_now - relativedelta.relativedelta(months=1)
        startdate = startdate.replace(day=1)

        # 個別請求書番号降順
        queryset = RequestResult.objects.filter()
        queryset = RequestResult.objects.order_by('InvoiceNUmber','DailyUpdateDate').reverse()
        # 削除済除外
        queryset = queryset.filter(is_Deleted=0,DailyUpdateDiv=1)
        # 発行日が前月月初か個別請求書未発行のもの
        #queryset = queryset.filter(Q(InvoiceIssueDate__gt=startdate) | Q(InvoiceIssueDiv=0))

        if query:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=query) | Q(OrderingId__CustomeCode__CustomerOmitName__icontains=query) |
                 Q(OrderingId__SupplierCode__CustomerOmitName__icontains=query) | Q(OrderingId__RequestCode__CustomerOmitName__icontains=query) | Q(OrderingId__ProductName__icontains=query) |
                 Q(OrderingId__RequestCode__CustomerOmitName__icontains=query) | Q(OrderingId__OrderNumber__icontains=query) | Q(OrderingId__OrderingCount__icontains=query)
            )

        if key:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=key) | Q(OrderingId__CustomeCode__CustomerOmitName__icontains=key) |
                 Q(OrderingId__SupplierCode__CustomerOmitName__icontains=key) | Q(OrderingId__RequestCode__CustomerOmitName__icontains=key) | Q(OrderingId__ProductName__icontains=key) |
                 Q(OrderingId__RequestCode__CustomerOmitName__icontains=key) | Q(OrderingId__OrderNumber__icontains=key) | Q(OrderingId__OrderingCount__icontains=key)
            )

        if word:
            queryset = queryset.filter(
                 Q(InvoiceNUmber__icontains=word) | Q(OrderingId__CustomeCode__CustomerOmitName__icontains=word) |
                 Q(OrderingId__SupplierCode__CustomerOmitName__icontains=word) | Q(OrderingId__RequestCode__CustomerOmitName__icontains=word) | Q(OrderingId__ProductName__icontains=word) |
                 Q(OrderingId__RequestCode__CustomerOmitName__icontains=word) | Q(OrderingId__OrderNumber__icontains=word) | Q(OrderingId__OrderingCount__icontains=word)
            )

        if InvoiceIssueDateFrom:
            queryset = queryset.filter(Q(InvoiceIssueDate__gte=(InvoiceIssueDateFrom)))

        return queryset

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
        
        form = IndividualSearchForm(initial=default_data) # 検索フォーム
        context['invsearch'] = form
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)
        return context