from django.shortcuts import render,redirect
from urllib.parse import urlencode
from django.views.generic import ListView,CreateView, UpdateView
from myapp.models import CustomerSupplier, OrderingTable
from myapp.form.forms import CustomerSupplierForm, CustomerSearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.views import viewsGetUrlFunction

# 検索機能のために追加
from django.db.models import Q
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

# 得意先仕入先マスター一覧/検索
class CustomerSupplierListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    context_object_name = 'object_list'
    queryset = CustomerSupplier.objects.order_by('CustomerCode')
    template_name = "crud/customersupplier/list/customersupplierlist.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
            self.request.GET.get('page_obj',None),
        ]
        request.session['cmsearch'] = search
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'cmsearch' in self.request.session:
            search = self.request.session['cmsearch']
            query = search[0]
        else:
            query = self.request.POST.get('query', None)

        # コード順
        queryset = CustomerSupplier.objects.order_by('CustomerCode')

        # 削除済除外
        queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                 Q(CustomerName__contains=query) | Q(Municipalities__contains=query) | Q(CustomerCode__contains=query) | Q(CustomerNameKana__contains=query) |
                 Q(Address__contains=query) | Q(PhoneNumber__contains=query) | Q(PrefecturesCode__prefecturename__icontains=query)| Q(ManagerCode__first_name__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        if 'cmsearch' in self.request.session:
            search = self.request.session['cmsearch']
            query = search[0]

        default_data = {'query': query}
        
        form = CustomerSearchForm(initial=default_data) # 検索フォーム
        context['cmsearch'] = form
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)
        return context
       
# 得意先仕入先マスター登録
class CustomerSupplierCreateView(LoginRequiredMixin,CreateView):
    model = CustomerSupplier
    form_class =  CustomerSupplierForm
    template_name = "crud/customersupplier/new/customersupplierform.html"

    def get(self, request):
        mngcode = self.request.user.id
        form = CustomerSupplierForm(self.request.POST or None,initial=
            {
            'PrefecturesCode': '1',
            'LastClaimBalance': 0,
            'LastReceivable': 0,
            'LastPayable': 0,
            'LastProceeds': 0,
            'ProceedsTarget': 0,
            'ManagerCode':mngcode,
            'OffsetDiv': 2,
            })

        context = {
            'form': form,
        }
        return render(request, 'crud/customersupplier/new/customersupplierform.html', context)

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            # Createid,Updatedidフィールドはログインしているユーザidとする
            post.Created_id = self.request.user.id
            post.Updated_id = self.request.user.id
            post.save()
        except Exception as e:
            message = "登録エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
        return redirect('myapp:list')
    # バリデーションエラー時
    def form_invalid(self, form):
        message = "エラーが発生しました"
        messages.error(self.request,message) 

        return super().form_invalid(form)

# 得意先仕入先マスター更新
class CustomerSupplierUpdateView(LoginRequiredMixin,UpdateView):
    model = CustomerSupplier
    form_class =  CustomerSupplierForm
    template_name = "crud/customersupplier/update/customersupplierformupdate.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['customerpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(CustomerSupplierUpdateView, self).get_context_data(**kwargs)
        context.update(dict(
            row=param,
            previewurl=self.request.session['customerpageno'])
            )

        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            if self.request.method == "POST":
                if form.is_valid():
                    post = form.save(commit=False)
                    # Updatedidフィールドはログインしているユーザidとする
                    post.Updated_id = self.request.user.id
                    post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    post.save()

                if 'customerpageno' in self.request.session:
                    incoming_url = self.request.session['customerpageno']
                    param=self.request.POST.get('row')
                    #listViewに戻るURLを取得
                    url = viewsGetUrlFunction.GetUrl(param, incoming_url)

                return redirect(url)
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['customerpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.session['customerpageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return super().form_invalid(form) 

# 得意先仕入先マスター削除
class CustomerSupplierDeleteView(LoginRequiredMixin,UpdateView):
    model = CustomerSupplier
    form_class =  CustomerSupplierForm
    template_name = "crud/customersupplier/delete/customersupplierformdelete.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['customerpageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
        #context
        context = super(CustomerSupplierDeleteView, self).get_context_data(**kwargs)
        context.update(dict(
            row=param,
            previewurl=self.request.session['customerpageno'])
            )

        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            if self.request.method == "POST":
                post = form.save(commit=False)
                pk=post.id
                Cnt = OrderingTable.objects.filter(
                    Q(DestinationCode=pk) |
                    Q(SupplierCode=pk) |
                    Q(ShippingCode=pk) |
                    Q(CustomeCode=pk) |
                    Q(RequestCode=pk) |
                    Q(StainShippingCode=pk) |
                    Q(ApparelCode=pk),
                    is_Deleted=0,
                    ).count()
                if Cnt > 0:
                    message = "受発注データが存在するため削除できません。"
                    logger.error(message)
                    messages.error(self.request,message) 
                    #ListViewに戻るときに色を付加する
                    incoming_url = self.request.session['customerpageno']
                    param=self.request.POST.get('row')
                    #listViewに戻るURLを取得
                    self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

                    return self.render_to_response(self.get_context_data(form=form))
    
                post.Updated_id = self.request.user.id
                post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                post.is_Deleted = True
                post.save()
            if 'customerpageno' in self.request.session:
                incoming_url = self.request.session['customerpageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                url = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return redirect(url)
        except Exception as e:
            message = self.request.id + "データの削除に失敗しました"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['customerpageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)
