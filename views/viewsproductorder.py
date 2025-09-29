from django.shortcuts import render,redirect
from django.views.generic import ListView,CreateView,UpdateView
from myapp.models import ProductOrder, ProductOrderDetail, CustomerSupplier, MerchandiseFileUpload
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.views import viewsGetUrlFunction
# ajax
from django.http import JsonResponse
# 検索機能のために追加
from django.db.models import Q
# forms
from myapp.form.formsproductorder import ProductOrderForm, ProductOrderFormset, SearchForm
# Transaction
from django.db import transaction
# SQL直接実行
from django.db import connection
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)
#Pagenation
from django.core.paginator import Page

# 受発注一覧/検索
class ProductOrderListView(LoginRequiredMixin,ListView):
    model = ProductOrder
    form_class = ProductOrderForm
    context_object_name = 'object_list'
    queryset = ProductOrder.objects.order_by('ProductOrderOrderingDate','Created_at').reverse()
    template_name = "crud/productorder/List/productorderlist.html"
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
            if 'posearch' in request.session:
                del request.session['posearch']
        else:
            request.session['posearch'] = search

        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'posearch' in self.request.session:
            search = self.request.session['posearch']
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

        # 依頼日、登録日大きい順で抽出
        queryset = ProductOrder.objects.order_by('ProductOrderOrderingDate','Created_at').reverse()
        # 削除済以外で担当者=ログインユーザ、管理者の場合は全レコード表示（削除済以外）
        if self.request.user.is_superuser == 0:
            # ログインユーザのみ一覧表示
            # queryset = queryset.filter(is_Deleted=0,ProductOrderManagerCode=self.request.user.id)
            # 全ユーザ表示
            queryset = queryset.filter(is_Deleted=0)
        else:
            queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                 Q(ProductOrderSlipDiv__contains=query) | Q(ProductOrderOrderNumber__contains=query) | Q(ProductOrderBrandName__contains=query) | 
                 Q(ProductOrderDestinationCode__CustomerOmitName__icontains=query) | Q(ProductOrderShippingCode__CustomerOmitName__icontains=query) | 
                 Q(ProductOrderSupplierCode__CustomerOmitName__icontains=query) | Q(ProductOrderApparelCode__CustomerOmitName__icontains=query) |
                 Q(ProductOrderApparelCode__CustomerOmitName__icontains=query) | Q(ProductOrderMarkName__contains=query) | 
                 Q(ProductOrderBrandName__contains=query) | Q(ProductOrderManagerCode__first_name__icontains=query) |
                 Q(ProductOrderMerchandiseCode__contains=query) | Q(id__contains=query) | Q(ProductOrderPartNumber__contains=query)
            )

        if key:
            queryset = queryset.filter(
                 Q(ProductOrderSlipDiv__contains=key) | Q(ProductOrderOrderNumber__contains=key) | Q(ProductOrderBrandName__contains=key) | 
                 Q(ProductOrderDestinationCode__CustomerOmitName__icontains=key) | Q(ProductOrderShippingCode__CustomerOmitName__icontains=key) |
                 Q(ProductOrderSupplierCode__CustomerOmitName__icontains=key) | Q(ProductOrderApparelCode__CustomerOmitName__icontains=key) |
                 Q(ProductOrderApparelCode__CustomerOmitName__icontains=key) | Q(ProductOrderMarkName__contains=key) | 
                 Q(ProductOrderBrandName__contains=key) | Q(ProductOrderManagerCode__first_name__icontains=key) |
                Q(ProductOrderMerchandiseCode__contains=key) | Q(id__contains=key) | Q(ProductOrderPartNumber__contains=key)
            )

        if word:
            queryset = queryset.filter(
                 Q(ProductOrderSlipDiv__contains=word) | Q(ProductOrderOrderNumber__contains=word) | Q(ProductOrderBrandName__contains=word) | 
                 Q(ProductOrderDestinationCode__CustomerOmitName__icontains=word) | Q(ProductOrderShippingCode__CustomerOmitName__icontains=word) |
                 Q(ProductOrderSupplierCode__CustomerOmitName__icontains=word) | Q(ProductOrderApparelCode__CustomerOmitName__icontains=word) |
                 Q(ProductOrderApparelCode__CustomerOmitName__icontains=word) | Q(ProductOrderMarkName__contains=word) | 
                 Q(ProductOrderBrandName__contains=word) | Q(ProductOrderManagerCode__first_name__icontains=word) |
                 Q(ProductOrderMerchandiseCode__contains=word) | Q(id__contains=word) | Q(ProductOrderPartNumber__contains=word)
            )

        if orderdateFrom and orderdateTo:
            queryset = queryset.filter(Q(ProductOrderDeliveryDate__range=(orderdateFrom,orderdateTo)))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        key = ''
        word = ''
        orderdateFrom = ''
        orderdateTo = ''
        if 'posearch' in self.request.session:
            search = self.request.session['posearch']
            query = search[0]
            key = search[1]
            word = search[2]
            orderdateFrom = search[3]
            orderdateTo = search[4]

        default_data = {'query': query,
                        'key': key,
                        'word': word,
                        'productorderdateFrom': orderdateFrom,
                        'productorderdateTo': orderdateTo,
                       }
        
        form = SearchForm(initial=default_data) # 検索フォーム
        context['posearch'] = form
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)
        return context

# 製品受発注情報登録
class ProductOrderCreateView(LoginRequiredMixin,CreateView):
    model = ProductOrder
    form_class =  ProductOrderForm
    formset_class =  ProductOrderFormset
    template_name = "crud/productorder/new/productorderform.html"
   
    def get(self, request):
        mngcode = self.request.user.id
        form = ProductOrderForm(self.request.POST or None,
                initial={'ProductOrderDestinationCode': '1',
                         'ProductOrderSupplierCode': '1',
                         'ProductOrderShippingCode': '1',
                         'ProductOrderCustomeCode': '1',
                         'ProductOrderRequestCode': '1',
                         'ProductOrderApparelCode': '1',
                         'ProductOrderManagerCode':mngcode,
                        })

        formset = ProductOrderFormset(self.request.POST or None)
        ProductOrderApparelCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        ProductOrderDestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        ProductOrderSupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(~Q(MasterDiv=2),is_Deleted=0).order_by('CustomerCode')
        ProductOrderShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)
        ProductOrderCustomeCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(~Q(MasterDiv=3),is_Deleted=0).order_by('CustomerCode')
        ProductOrderRequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0)

        context = {
            'form': form,
            'formset': formset,
            'ProductOrderApparelCode': ProductOrderApparelCode,
            'ProductOrderDestinationCode': ProductOrderDestinationCode,
            'ProductOrderSupplierCode':ProductOrderSupplierCode,
            'ProductOrderShippingCode':ProductOrderShippingCode,
            'ProductOrderCustomeCode':ProductOrderCustomeCode,
            'ProductOrderRequestCode':ProductOrderRequestCode,
        }

        return render(request, 'crud/productorder/new/productorderform.html', context)

    
    def exec_ajax(request):
        if request.method == 'GET':  # GETの処理
            param = request.GET.get("param")  # GETパラメータ
            # カラーとサイズを取得する
            def dictfetchall(cursor):
                "Return all rows from a cursor as a dict"
                columns = [col[0] for col in cursor.description]
                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            # カラーとサイズを取得するSQL
            with connection.cursor() as cursor:
                cursor.execute(
                                " select "
                                    "a.Mcdcolorid_id   AS Mcdcolorid_id, "
                                    "a.McdColor        AS McdColor, "
                                    "b.mcdsize         AS McdSize, "
                                    "a.id              AS id, "
                                    "b.id              AS McdSizeid, "
                                    "d.McdPartNumber   AS McdPartNumber, "
                                    "a.McdColorNumber  AS McdColorNumber "
                                " from " 
                                    "myapp_merchandisecolor a " 
                                    "INNER JOIN "
                                    "myapp_merchandisesize b on "
                                        "a.McdColorId_id = b.McdSizeId_id "
                                    " left join "
                                    " myapp_Merchandise d on "
                                        " d.id = a.McdColorId_id"
                                " where " 
                                "     a.Mcdcolorid_id = %s "
                                " and a.is_Deleted = 0 "
                                " and b.is_Deleted = 0 "
                                " order by "
                                "    a.id, "
                                "    b.id "
                            , [str(param)])
                colorsize = dictfetchall(cursor)

            context = {
                'list': colorsize,
            }

            return JsonResponse(context)

    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = ProductOrderFormset(self.request.POST,instance=post)

            if self.request.method == 'POST':          
                if form.is_valid():
                    post.ProductOrderOrderNumber = post.ProductOrderOrderNumber.zfill(7)
                    post.Created_id = self.request.user.id
                    post.Updated_id = self.request.user.id
                    post.save()      

                if formset.is_valid():
                    instances = formset.save(commit=False)
                    # 明細のfileを取り出して更新
                    for file in instances:
                        file.Created_id = self.request.user.id
                        file.Updated_id = self.request.user.id
                        file.save()
            else:
                message = "登録エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 
                return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))
            return redirect('myapp:productorderlist')
        except Exception as e:
            message = "登録エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "登録エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        return self.render_to_response(self.get_context_data(form=form))

class ProductOrderUpdateView(LoginRequiredMixin,UpdateView):
    model = ProductOrder
    form_class =  ProductOrderForm
    formset_class =  ProductOrderFormset
    template_name = "crud/productorder/update/productorderformupdate.html" 
   
    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['productpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
        #画像ファイル
        code = ProductOrder.objects.values_list('ProductOrderMerchandiseCode', flat=True).get(id=pk,is_Deleted=0)
        profile = MerchandiseFileUpload.objects.filter(McdDtuploadid=str(code),is_Deleted=0)

        context = super(ProductOrderUpdateView, self).get_context_data(**kwargs)

        # カラーとサイズを取得する
        def dictfetchall(cursor):
            "Return all rows from a cursor as a dict"
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        # カラーとサイズを取得するSQL
        with connection.cursor() as cursor:
            cursor.execute(
                            " select "
                                "  a.id "
                                " ,a.podcolorid_id "
                                " ,b.McdColor "
                                " ,a.podsizeid_id "
                                " ,c.McdSize "
                                " ,a.PodVolume"
                                " ,b.McdColorNumber "
                            " from " 
                                " myapp_productorderdetail a "
                                " left join " 
                                " myapp_merchandisecolor b on "
                                    " a.PodColorId_id = b.id "
                                " left join "
                                " myapp_merchandisesize c on "
                                    " a.PodsizeId_id = c.id "
                            " where "
                                "     a.PodDetailId_id = %s "
                                " and b.is_Deleted = 0 "
                                " and c.is_Deleted = 0 "
                        , [str(pk)])
            colorsize = dictfetchall(cursor)

        context.update(dict(formset=ProductOrderFormset(self.request.POST or None, instance=self.get_object(), queryset=ProductOrderDetail.objects.filter(is_Deleted=0))),
                            ProductOrderApparelCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                            ProductOrderDestinationCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                            ProductOrderSupplierCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                            ProductOrderShippingCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                            ProductOrderCustomeCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0).order_by('CustomerCode'),
                            ProductOrderRequestCode = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('CustomerCode').filter(is_Deleted=0),
                            row=param,
                            previewurl=self.request.session['productpageno'],
                            images=profile,
                        )      
        context.update(list=colorsize) 

        return context

    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = ProductOrderFormset(self.request.POST,instance=post)

            if self.request.method == 'POST':          
                if form.is_valid():
                    #post.ProductOrderOrderNumber = post.ProductOrderOrderNumber.zfill(7)
                    post.Updated_id = self.request.user.id
                    post.save()      

                if formset.is_valid():
                    instances = formset.save(commit=False)
                    # 明細のfileを取り出して更新
                    for file in instances:
                        file.Updated_id = self.request.user.id
                        file.save()
            else:
                message = "更新エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 
                #ListViewに戻るときに色を付加する
                incoming_url = self.request.session['productpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

                return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))

            if 'productpageno' in self.request.session:
                incoming_url = self.request.session['productpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                url = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return redirect(url)
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['productpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.session['productpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form))

class ProductOrderDeleteView(LoginRequiredMixin,UpdateView):
    model = ProductOrder
    form_class =  ProductOrderForm
    formset_class =  ProductOrderFormset
    template_name = "crud/productorder/Delete/productorderformdelete.html" 
   
    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        pk = self.kwargs.get("pk")
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['productpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(ProductOrderDeleteView, self).get_context_data(**kwargs)
        # カラーとサイズを取得する
        def dictfetchall(cursor):
            "Return all rows from a cursor as a dict"
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        # カラーとサイズを取得するSQL
        with connection.cursor() as cursor:
            cursor.execute(
                            " select "
                                " a.id "
                                " ,a.podcolorid_id "
                                " ,b.McdColor "
                                " ,a.podsizeid_id "
                                " ,c.McdSize "
                                " ,a.PodVolume"
                                " ,b.McdColorNumber "
                            " from " 
                                " myapp_productorderdetail a "
                                " left join " 
                                " myapp_merchandisecolor b on "
                                    " a.PodColorId_id = b.id "
                                " left join "
                                " myapp_merchandisesize c on "
                                    " a.PodsizeId_id = c.id "
                                " left join "
                                " myapp_Merchandise d on "
                                    " d.id = b.McdColorId_id"
                            " where "
                                " a.PodDetailId_id = %s "
                        , [str(pk)])
            colorsize = dictfetchall(cursor)

        context.update(dict(formset=ProductOrderFormset(self.request.POST or None, instance=self.get_object(), queryset=ProductOrderDetail.objects.filter(is_Deleted=0)),
                            row=param,
                            previewurl=self.request.session['productpageno'],
                            ))      
        context.update(list=colorsize) 

        return context
    
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        post = form.save(commit=False)
        formset = ProductOrderFormset(self.request.POST,instance=post)

        if self.request.method == 'POST':          
            if form.is_valid():
                post.is_Deleted = True
                post.Updated_id = self.request.user.id
                post.save()      

            if formset.is_valid():
                instances = formset.save(commit=False)
                # 削除チェックがついたfileを取り出して削除
                for file in instances:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()
        else:
            message = "削除できませんでした"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['productpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class))

        if 'productpageno' in self.request.session:
            incoming_url = self.request.session['productpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            url = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return redirect(url)
    # バリデーションエラー時
    def form_invalid(self, form):
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.session['productpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form))