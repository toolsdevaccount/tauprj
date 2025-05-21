from django.shortcuts import render,redirect
from django.views.generic import ListView,CreateView,UpdateView
from myapp.models import Consumetax,CustomerSupplier
from myapp.form.formsconsumetax import ConsumetaxForm, ConsumetaxSearchForm
from django.contrib.auth.mixins import LoginRequiredMixin
# 検索機能のために追加
from django.db.models import Q
# Transaction
from django.db import transaction
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

# 消費税率情報一覧/検索
class ConsumetaxListView(LoginRequiredMixin,ListView):
    model = Consumetax
    context_object_name = 'object_list'
    queryset = Consumetax.objects.order_by('id').reverse()
    template_name = "crud/consumetax/list/consumetaxlist.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
        ]
        request.session['pysearch'] = search
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'consearch' in self.request.session:
            search = self.request.session['consearch']
            query = search[0]
        else:
            query = self.request.POST.get('query', None)

        # コード順
        queryset = Consumetax.objects.order_by('id')
        # 削除済除外
        queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                Q(TaxRate__icontains=query) | Q(id__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        if 'consearch' in self.request.session:
            search = self.request.session['consearch']
            query = search[0]

        default_data = {'query': query }
        
        form = ConsumetaxSearchForm(initial=default_data) # 検索フォーム
        context['consearch'] = form
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)
        return context
       
# 消費税率情報登録
class ConsumetaxCreateView(LoginRequiredMixin,CreateView):
    model = Consumetax
    form_class =  ConsumetaxForm
    template_name = "crud/consumetax/new/consumetaxform.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        context = super(ConsumetaxCreateView, self).get_context_data(**kwargs)
        context.update()
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            if self.request.method == 'POST':            
                if form.is_valid():
                    # Created_id,Updated_idフィールドはログインしているユーザidとする
                    post.Created_id = self.request.user.id
                    post.Updated_id = self.request.user.id
                    post.Created_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    post.save()       
            else:
                # is_validがFalseの場合はエラー文を表示
                message = "登録エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 

                return self.render_to_response(self.get_context_data(form=form))
            return redirect('myapp:consumetaxlist')
        except Exception as e:
            message = "登録エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "登録エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        return super().form_invalid(form)

# 消費税率情報更新
class ConsumetaxUpdateView(LoginRequiredMixin,UpdateView):
    model = Consumetax
    form_class =  ConsumetaxForm
    template_name = "crud/consumetax/update/consumetaxformupdate.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        self.request.session['consumetaxpageno'] = self.request.META['HTTP_REFERER']
        context = super(ConsumetaxUpdateView, self).get_context_data(**kwargs)
        context.update()
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        try:
            if self.request.method == "POST":
                if form.is_valid():
                    post = form.save(commit=False)
                    # Updatedidフィールドはログインしているユーザidとする
                    post.Updated_id = self.request.user.id
                    post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    post.save()
                if 'consumetaxpageno' in self.request.session:
                    incoming_url = self.request.session['consumetaxpageno']

                return redirect(incoming_url)
                #return redirect('myapp:Paymentlist')
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            #戻るURLにListViewのセッションの値を設定
            self.request.META['HTTP_REFERER'] = self.request.session['consumetaxpageno']

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message)
        #戻るURLにListViewのセッションの値を設定
        self.request.META['HTTP_REFERER'] = self.request.session['paymentpageno']

        return super().form_invalid(form) 

# 消費税率情報削除
class ConsumetaxDeleteView(LoginRequiredMixin,UpdateView):
    model = Consumetax
    form_class =  ConsumetaxForm
    template_name = "crud/consumetax/delete/consumetaxformdelete.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        self.request.session['consumetaxpageno'] = self.request.META['HTTP_REFERER']
        context = super(ConsumetaxDeleteView, self).get_context_data(**kwargs)
        context.update()
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        if self.request.method == "POST":
            post = form.save(commit=False)
 
            post.Updated_id = self.request.user.id
            post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
            post.is_Deleted = True
            post.save()
        if 'consumetaxpageno' in self.request.session:
            incoming_url = self.request.session['consumetaxpageno']

        return redirect(incoming_url)
        #return redirect('myapp:Paymentlist')

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "削除できませんでした"
        logger.error(message)
        messages.error(self.request,message) 
        #戻るURLにListViewのセッションの値を設定
        self.request.META['HTTP_REFERER'] = self.request.session['consumetaxpageno']

        return super().form_invalid(form) 
