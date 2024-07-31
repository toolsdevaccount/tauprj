from typing import Any
from django.shortcuts import render,redirect
from urllib.parse import urlencode
from django.views.generic import ListView,CreateView,UpdateView
from myapp.models import OrderingTable, OrderingDetail, CustomerSupplier,RequestResult
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.form.forms import OrderingForm,OrderingFormset, SearchForm
from myapp.views import viewsGetUrlFunction
# 検索機能のために追加
from django.db.models import Q
# 日時
from django.utils import timezone
import datetime
# Transaction
from django.db import transaction
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class OrderingListView(LoginRequiredMixin,ListView):
    model = OrderingTable
    form_class = OrderingForm
    context_object_name = 'object_list'
    queryset = OrderingTable.objects.order_by('OrderingDate','Created_at').reverse()
    template_name = "crud/ordering/list/orderinglist.html"
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
            del request.session['search']
        else:
            request.session['search'] = search

        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'search' in self.request.session:
            search = self.request.session['search']
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
            # ログインユーザのみ一覧表示
            #queryset = queryset.filter(is_Deleted=0,Created_id=self.request.user.id)
            # 全ユーザ表示
            queryset = queryset.filter(is_Deleted=0)
        else:
            queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                 Q(SlipDiv__contains=query) | Q(OrderNumber__contains=query) | Q(ProductName__contains=query) | Q(MarkName__contains=query) |
                 Q(DestinationCode__CustomerOmitName__icontains=query) | Q(ShippingCode__CustomerOmitName__icontains=query) | 
                 Q(SampleDiv__divname__icontains=query) | Q(RequestCode__CustomerOmitName__icontains=query) | 
                 Q(ManagerCode__first_name__icontains=query) | Q(OutputDiv__outputdivname__icontains=query)
            )
        if key:
            queryset = queryset.filter(
                 Q(SlipDiv__contains=key) | Q(OrderNumber__contains=key) | Q(ProductName__contains=key) | Q(MarkName__contains=key) |
                 Q(DestinationCode__CustomerOmitName__icontains=key) | Q(ShippingCode__CustomerOmitName__icontains=key) |
                 Q(SampleDiv__divname__icontains=key) | Q(RequestCode__CustomerOmitName__icontains=key) |
                 Q(ManagerCode__first_name__icontains=key) | Q(OutputDiv__outputdivname__icontains=key)
            )

        if word:
            queryset = queryset.filter(
                 Q(SlipDiv__contains=word) | Q(OrderNumber__contains=word) | Q(ProductName__contains=word) | Q(MarkName__contains=word) |
                 Q(DestinationCode__CustomerOmitName__icontains=word) | Q(ShippingCode__CustomerOmitName__icontains=word) | 
                 Q(SampleDiv__divname__icontains=word) | Q(RequestCode__CustomerOmitName__icontains=word) | 
                 Q(ManagerCode__first_name__icontains=word) | Q(OutputDiv__outputdivname__icontains=word)
            )

        if orderdateFrom and orderdateTo:
            queryset = queryset.filter(Q(OrderingDate__range=(orderdateFrom,orderdateTo)))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = ''
        key = ''
        word = ''
        orderdateFrom = ''
        orderdateTo = ''
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        if 'search' in self.request.session:
            search = self.request.session['search']
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
        context['search'] = form
        return context

# 受発注情報登録
class OrderingCreateView(LoginRequiredMixin,CreateView):
    model = OrderingTable
    form_class =  OrderingForm
    formset_class = OrderingFormset
    template_name = "crud/ordering/new/orderingform.html"
   
    # get_initialをオーバーライド
    def get_initial(self):
        mngcode = self.request.user.id

        initial = super(OrderingCreateView,self).get_initial()
        initial['ManagerCode'] = mngcode

        return initial

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        context = super(OrderingCreateView, self).get_context_data(**kwargs)
        context.update(dict(formset=OrderingFormset(self.request.POST or None, initial=[{'DetailUnitDiv':0,}])),
                DestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                SupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(~Q(MasterDiv=2),is_Deleted=0).order_by('CustomerCode'),
                ShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                CustomerCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(~Q(MasterDiv=3),is_Deleted=0).order_by('CustomerCode'),
                RequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                StainShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                ApparelCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                )
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = OrderingFormset(self.request.POST,instance=post) 
            if self.request.method == 'POST' and formset.is_valid(): 
                instances = formset.save(commit=False)
                
                if form.is_valid():
                    post.OrderNumber = post.OrderNumber.zfill(7)
                    # Created_id,Updated_idフィールドはログインしているユーザidとする
                    post.Created_id = self.request.user.id
                    post.Updated_id = self.request.user.id
                    post.save()
            
                    for file in instances:
                        file.DetailItemNumber = file.DetailItemNumber.zfill(4)
                        file.Created_id = self.request.user.id
                        file.Updated_id = self.request.user.id
                        file.save()
            else:
                # is_validがFalseの場合はエラー文を表示
                message = "登録エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 
                return self.render_to_response(self.get_context_data(form=form, formset=formset))

            return redirect('myapp:orderinglist')
        except Exception as e:
            message = "登録エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 

    # バリデーションエラー時
    def form_invalid(self,form):
        # セッションにデータを格納
        self.request.session['form_data'] = self.request.POST

        #context = self.get_context_data(form=form)
        #context["DestinationCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        #context["SupplierCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode')
        #context["ShippingCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        #context["CustomerCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode')
        #context["RequestCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        #context["StainShippingCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        #context["ApparelCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)


        message = "登録エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #return self.render_to_response(context)

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))

# 受発注情報編集
class orderingUpdateView(LoginRequiredMixin,UpdateView):
    model = OrderingTable
    form_class =  OrderingForm
    formset_class = OrderingFormset
    template_name = "crud/ordering/update/orderingformupdate.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        ####
        pk = self.kwargs.get("pk")
        queryset = RequestResult.objects.filter(is_Deleted=0, OrderingId_id=pk)
        ####

        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['oredringpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(orderingUpdateView, self).get_context_data(**kwargs)
        context.update(dict(formset=OrderingFormset(self.request.POST or None, instance=self.get_object(), queryset=OrderingDetail.objects.filter(is_Deleted=0))),
                       DestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       SupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       ShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       CustomerCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       RequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       StainShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       ApparelCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       row=param,
                       previewurl=self.request.session['oredringpageno'],
                    )

        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = OrderingFormset(self.request.POST,instance=post) 

            if self.request.method == 'POST' and formset.is_valid(): 
                instances = formset.save(commit=False)
            
                if form.is_valid():
                    post.OrderNumber = post.OrderNumber.zfill(7)
                    # Updated_idフィールドはログインしているユーザidとする
                    post.Updated_id = self.request.user.id
                    # Updated_atは現在日付時刻とする
                    post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時               
                    post.save()

                    # 削除チェックがついたfileを取り出して更新
                    for file in formset.deleted_objects:
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.is_Deleted = True
                        file.save()

                    # 明細のfileを取り出して更新
                    for file in instances:
                        file.DetailItemNumber = file.DetailItemNumber.zfill(4)
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.save()
            else:
                message = "更新エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message)
                #ListViewに戻るときに色を付加する
                incoming_url = self.request.session['oredringpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
 
                return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class)) 

            if 'oredringpageno' in self.request.session:
                incoming_url = self.request.session['oredringpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                url = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return redirect(url)
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['oredringpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

    # バリデーションエラー時
    def form_invalid(self,form):
        context = self.get_context_data(form=form)
        #context["formset"] = dict(formset=OrderingFormset(self.request.POST or None, instance=self.get_object(), queryset=OrderingDetail.objects.filter(is_Deleted=0)))
        context["DestinationCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        context["SupplierCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode')
        context["ShippingCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        context["CustomerCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode')
        context["RequestCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        context["StainShippingCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        context["ApparelCode"] = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)

        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.session['oredringpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(context)


# 受発注情報削除
class orderingDeleteView(LoginRequiredMixin,UpdateView):
    model = OrderingTable
    form_class =  OrderingForm
    formset_class = OrderingFormset
    template_name = "crud/ordering/delete/orderingformdelete.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['oredringpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(orderingDeleteView, self).get_context_data(**kwargs)
        context.update(dict(formset=OrderingFormset(self.request.POST or None, instance=self.get_object(), queryset=OrderingDetail.objects.filter(is_Deleted=0))),
                       DestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       SupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       ShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       CustomerCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                       RequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       StainShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       ApparelCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                       row=param,
                       previewurl=self.request.session['oredringpageno'],
                       )
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        post = form.save(commit=False)
        formset = OrderingFormset(self.request.POST,instance=post) 
        pk = self.kwargs.get("pk")
        ReqCnt = RequestResult.objects.filter(is_Deleted=0,OrderingId_id=pk).count()
        if ReqCnt > 0:
            message = "実績が存在するため削除できません。実績を削除してください。"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['oredringpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))

        if self.request.method == 'POST':           
            instances = formset.save(commit=False)
            if form.is_valid():
                post.is_Deleted = True
                # Updated_idフィールドはログインしているユーザidとする
                post.Updated_id = self.request.user.id
                # Updated_atは現在日付時刻とする
                post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時               
                post.save()

            if formset.is_valid():
                # 明細のfileを取り出して削除
                for file in instances:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()
        else:
            #戻るURLにListViewのセッションの値を設定
            self.request.META['HTTP_REFERER'] = self.request.session['oredringpageno']

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))        
        if 'oredringpageno' in self.request.session:
            incoming_url = self.request.session['oredringpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            url = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return redirect(url)

    # バリデーションエラー時
    def form_invalid(self,form):
        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.session['oredringpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))        