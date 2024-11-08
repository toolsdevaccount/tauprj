from django.shortcuts import redirect, HttpResponse
from django.views.generic import ListView, UpdateView
from myapp.models import OrderingTable, OrderingDetail, CustomerSupplier, RequestResult
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.form.formsrequestresult import RequestResultForm, RequestRecordFormset, RequestResultFormset, SearchForm
from myapp.views import viewsGetUrlFunction
# 検索機能のために追加
from django.db.models import Q, FilteredRelation

# 日時
from django.utils import timezone
import datetime
# Transaction
from django.db import transaction
# ajax
from django.http import JsonResponse
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class RequestResultListView(LoginRequiredMixin,ListView):
    model = OrderingTable
    form_class = RequestResultForm
    context_object_name = 'object_list'
    queryset = OrderingDetail.objects.select_related()
    template_name = "crud/requestresult/list/requestresultlist.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
            self.request.POST.get('key', None),
            self.request.POST.get('word', None),
            self.request.POST.get('orderdateFrom', None),
            self.request.POST.get('orderdateTo', None),
        ]

        if 'clear' in request.POST:
            del request.session['rqsearch']
        else:
            request.session['rqsearch'] = search

        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'rqsearch' in self.request.session:
            search = self.request.session['rqsearch']
            query = search[0]
            key = search[1]
            word = search[2]
            orderdateFrom = search[3]
            orderdateTo = search[4]
        else:
            query = self.request.POST.get('query', None)
            key = self.request.POST.get('key', None)
            word = self.request.POST.get('word', None)
            orderdateFrom = self.request.POST.get('orderdateFrom', None)
            orderdateTo = self.request.POST.get('orderdateTo', None)

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
                Q(SlipDiv__contains=query) | Q(OrderNumber__contains=query) | Q(DestinationCode__CustomerOmitName__icontains=query) |
                Q(ProductName__contains=query) | Q(ShippingCode__CustomerOmitName__icontains=query) | Q(RequestCode__CustomerOmitName__icontains=query)               
            )
        if key:
            queryset = queryset.filter(
                Q(SampleDiv__divname__icontains=key) | Q(OutputDiv__outputdivname__icontains=key) | Q(ManagerCode__first_name__icontains=key) |
                Q(SlipDiv__contains=key) | Q(OrderNumber__contains=key) | Q(DestinationCode__CustomerOmitName__icontains=key) |
                Q(ProductName__contains=key) | Q(ShippingCode__CustomerOmitName__icontains=key) | Q(RequestCode__CustomerOmitName__icontains=key)
            )

        if word:
            queryset = queryset.filter(
                Q(SampleDiv__divname__icontains=word) | Q(OutputDiv__outputdivname__icontains=word) | Q(ManagerCode__first_name__icontains=word) |
                Q(SlipDiv__contains=word) | Q(OrderNumber__contains=word) | Q(DestinationCode__CustomerOmitName__icontains=word) |
                Q(ProductName__contains=word) | Q(ShippingCode__CustomerOmitName__icontains=word) | Q(RequestCode__CustomerOmitName__icontains=word)
            )

        if orderdateFrom and orderdateTo:
            queryset = queryset.filter(Q(OrderingDate__range=(orderdateFrom,orderdateTo)))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        key = ''
        word = ''
        orderdateFrom = ''
        orderdateTo = ''
        if 'rqsearch' in self.request.session:
            search = self.request.session['rqsearch']
            query = search[0]
            key = search[1]
            word = search[2]
            orderdateFrom = search[3]
            orderdateTo = search[4]

        default_data = {'query': query,
                        'key': key,
                        'word': word,
                        'orderdateFrom': orderdateFrom,
                        'orderdateTo': orderdateTo,
                       }
        
        form = SearchForm(initial=default_data) # 検索フォーム
        context['rqsearch'] = form
        return context

# 受発注情報編集
class RequestResultUpdateView(LoginRequiredMixin,UpdateView):
    model = OrderingTable
    form_class =  RequestResultForm
    formset_class = RequestResultFormset
    inlinesRecord_class = RequestRecordFormset
    template_name = "crud/requestresult/update/requestresultformupdate.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        queryset = RequestResult.objects.filter(is_Deleted=0, OrderingId_id=pk)
        key = queryset.values_list("OrderingDetailId_id",flat=True).first()

        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['requestpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
       
        context = super(RequestResultUpdateView, self).get_context_data(**kwargs)
        context.update(dict(
                       formset=RequestResultFormset(self.request.POST or None, instance=self.get_object(), queryset=OrderingDetail.objects.filter(OrderingTableId_id=pk,is_Deleted=0))),
                       inlinesRecord=RequestRecordFormset(self.request.POST or None, instance=self.get_object(), queryset=RequestResult.objects.filter(is_Deleted=0, OrderingDetailId_id=key)),
                       previewurl=self.request.session['requestpageno'],
                       row=param,
                       )

        return context

    def exec_ajax_result(request):
        if request.method == 'GET':  # GETの処理
            param = request.GET.get("param")  # GETパラメータ
            detail = RequestResult.objects.values(
                'id',
                'ResultItemNumber',
                'ResultDate',
                'ShippingDate',
                'ShippingVolume',
                'SlipNumber',
                'ResultSummary',
                'ResultMoveDiv',
                'ResultGainDiv',
                'ResultDecreaseDiv',
                'OrderingDetailId_id',  
            ).filter(
                OrderingDetailId_id=param,
                is_Deleted=0,
            )

            context = {
                'list': list(detail),
            }

            return JsonResponse(context)

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定   
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            inlinesRecord = RequestRecordFormset(self.request.POST,instance=post)
            
            if self.request.method == 'POST' and inlinesRecord.is_valid():
                if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    if inlinesRecord.is_valid():
                        instances = inlinesRecord.save(commit=False)
                        # 明細のfileを取り出して更新
                        for file in instances:
                            file.Created_id = self.request.user.id
                            file.Updated_id = self.request.user.id
                            file.Created_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                            file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                            file.save()
                        # 削除チェックがついたfileを取り出して更新
                        for file in inlinesRecord.deleted_objects:
                            file.Updated_id = self.request.user.id
                            file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                            file.is_Deleted = True
                            file.save()
            else:
                # is_validがFalseの場合はエラー文を表示
                message = "更新エラーが発生しました.\n入力値を確認してください."
                logger.error(message)
                #ListViewに戻るときに色を付加する
                incoming_url = self.request.session['requestpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

                return HttpResponse(message, status=400, content_type='application/json')

            message = "更新が正常に終了しました"
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['requestpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
            dict = {
                    "answer": message,
                    }

            return JsonResponse(dict)
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            #messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['requestpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            #return JsonResponse(message, safe=False)
            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class)) 

    # バリデーションエラー時
    def form_invalid(self,form):
        incoming_url = self.request.session['requestpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class)) 

# 受発注情報削除
class RequestResultDeleteView(LoginRequiredMixin,UpdateView):
    model = OrderingTable
    form_class =  RequestResultForm
    formset_class = RequestResultFormset
    template_name = "crud/requestresult/delete/requestresultformdelete.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        context = super(RequestResultDeleteView, self).get_context_data(**kwargs)
        context.update(dict(formset=RequestResultFormset(self.request.POST or None, instance=self.get_object(), queryset=OrderingDetail.objects.filter(is_Deleted=0))),
                       DestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       SupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       ShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       CustomerCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       RequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       StainShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       )
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        post = form.save(commit=False)
        formset = RequestResultFormset(self.request.POST,instance=post) 

        if self.request.method == 'POST':           
            if form.is_valid():
                post.is_Deleted = True
                # Updated_idフィールドはログインしているユーザidとする
                post.Updated_id = self.request.user.id
                # Updated_atは現在日付時刻とする
                post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時               
                post.save()

            if formset.is_valid():
                instances = formset.save(commit=False)
                # 明細のfileを取り出して削除
                for file in instances:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()
        else:
            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))        
        return redirect('myapp:requestresultlist')

    # バリデーションエラー時
    def form_invalid(self,form):
        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))        