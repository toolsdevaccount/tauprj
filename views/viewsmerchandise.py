from django.shortcuts import render, redirect
from urllib.parse import urlencode
from django.views.generic import ListView,CreateView,UpdateView
from myapp.models import Merchandise,MerchandiseDetail, MerchandiseColor, MerchandiseSize, MerchandiseFileUpload, ProductOrder
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.views import viewsGetUrlFunction
# 検索機能のために追加
from django.db.models import Q
# 日時
from django.utils import timezone
import datetime
# forms
from myapp.form.formsmerchandise import MerchandiseForm, MerchandiseFormset, MerchandiseColorFormset, MerchandiseSizeFormset, MerchandisefileFormset, SearchForm
# Transaction
from django.db import transaction
# fileupload
from django.conf import settings
#from django.core.files.storage import FileSystemStorage

# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 商品一覧/検索
class MerchandiseListView(LoginRequiredMixin,ListView):
    model = Merchandise
    form_class = MerchandiseForm
    context_object_name = 'object_list'
    queryset = Merchandise.objects.order_by('id').reverse()
    template_name = "crud/merchandise/list/merchandiselist.html"
    paginate_by = 20

    def post(self, request, *args, **kwargs):
        search = [
            self.request.POST.get('query', None),
        ]
        request.session['mdsearch'] = search
        # 検索時にページネーションに関連したエラーを防ぐ
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    #検索機能
    def get_queryset(self):
        if 'mdsearch' in self.request.session:
            search = self.request.session['mdsearch']
            query = search[0]
        else:
            query = self.request.POST.get('query', None)

        # 商品コード大きい順で抽出
        queryset = Merchandise.objects.order_by('id').reverse()
        # 削除済以外、管理者の場合は全レコード表示（削除済以外）
        if self.request.user.is_superuser == 0:
            # ログインユーザのみ一覧表示
            #queryset = queryset.filter(is_Deleted=0,McdManagerCode=self.request.user.id)
            # 全ユーザ表示
            queryset = queryset.filter(is_Deleted=0)
        else:
            queryset = queryset.filter(is_Deleted=0)

        if query:
            queryset = queryset.filter(
                Q(id__contains=query) | Q(McdTempPartNumber__contains=query) | Q(McdPartNumber__contains=query) | Q(McdManagerCode__first_name__icontains=query)  
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        query = ''
        if 'mdsearch' in self.request.session:
            search = self.request.session['mdsearch']
            query = search[0]

        default_data = {'query': query }
        
        form = SearchForm(initial=default_data) # 検索フォーム
        context['mdsearch'] = form

        return context

# 商品情報登録
class MerchandiseCreateView(LoginRequiredMixin,CreateView):
    model = Merchandise
    form_class =  MerchandiseForm
    formset_class = MerchandiseFormset
    inlinescolor_class = MerchandiseColorFormset
    inlinessize_class = MerchandiseSizeFormset
    inlinesfile_class = MerchandisefileFormset
    template_name = "crud/merchandise/new/merchandiseform.html"
   
    def get(self, request):
        try:
            mngcode = self.request.user.id
            form = MerchandiseForm(self.request.POST or None, 
                                initial={
                                        'McdTreatmentCode': '1',
                                        'McdManagerCode': mngcode,
                                        'McdUnitCode':'1',
                                        'McdProcessCode':'1',
                                        })
            formset = MerchandiseFormset
            inlinescolor = MerchandiseColorFormset
            inlinessize = MerchandiseSizeFormset
            inlinesfile = MerchandisefileFormset

            context = {
                'form': form,
                'formset': formset,
                'inlinescolor': inlinescolor,
                'inlinessize': inlinessize,
                'inlinesfile': inlinesfile,
            }

            return render(request, 'crud/merchandise/new/merchandiseform.html', context)
        except Exception as e:
            message = "データの呼び出しに失敗しました"
            logger.error(message)
            messages.error(self.request,message) 

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        context = super(MerchandiseCreateView, self).get_context_data(**kwargs)
        context.update(dict(formset=MerchandiseFormset(self.request.POST or None)),
                inlinescolor = MerchandiseColorFormset(self.request.POST or None),
                inlinessize = MerchandiseSizeFormset(self.request.POST or None),
                inlinesfile = MerchandisefileFormset(self.request.POST or None),
                )

        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = MerchandiseFormset(self.request.POST,instance=post) 
            inlinescolor = MerchandiseColorFormset(self.request.POST,instance=post)
            inlinessize = MerchandiseSizeFormset(self.request.POST,instance=post)
            inlinesfile = MerchandisefileFormset(self.request.POST or None, files=self.request.FILES or None, instance=post)

            if self.request.method == 'POST' and formset.is_valid() and inlinescolor.is_valid() and inlinessize.is_valid():
                instances = formset.save(commit=False)
                instancecolor = inlinescolor.save(commit=False)
                instancesize = inlinessize.save(commit=False)
                #アップロードファイルの存在確認
                if inlinesfile.files!={}:
                    if inlinesfile.errors:
                        for errmessage in inlinesfile.errors:
                            if errmessage:
                                message = errmessage
                                logger.error(message)
                                messages.error(self.request,message) 

                                return self.render_to_response(self.get_context_data(form=form, formset=formset, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile,))
                    instancefile = inlinesfile.save(commit=False)
                
                with transaction.atomic():
                    if form.is_valid():
                        # Created_id,Updated_idフィールドはログインしているユーザidとする
                        post.Created_id = self.request.user.id
                        post.Updated_id = self.request.user.id
                        post.save()
                
                    if formset.is_valid():
                        for file in instances:
                            file.Created_id = self.request.user.id
                            file.Updated_id = self.request.user.id
                            file.save()

                    if inlinescolor.is_valid():
                        for file in instancecolor:
                            file.Created_id = self.request.user.id
                            file.Updated_id = self.request.user.id
                            file.save()

                    if inlinessize.is_valid():
                        for file in instancesize:
                            file.Created_id = self.request.user.id
                            file.Updated_id = self.request.user.id
                            file.save()

                    if inlinesfile.files !={}:
                        if inlinesfile.is_valid():
                            for file in instancefile:
                                file.Created_id = self.request.user.id
                                file.Updated_id = self.request.user.id
                                file.save()
            else:
                # is_validがFalseの場合はエラー文を表示
                message = "エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 

                return self.render_to_response(self.get_context_data(form=form, formset=formset, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile,))
    
            return redirect('myapp:merchandiselist')
        except Exception as e:
            message = "登録エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile))

    # バリデーションエラー時
    def form_invalid(self, form):
        message = "登録エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=self.inlinescolor_class, inlinessize=self.inlinessize_class, inlinesfile=self.inlinesfile_class))

# 商品情報編集
class MerchandiseUpdateView(LoginRequiredMixin,UpdateView):
    model = Merchandise
    form_class =  MerchandiseForm
    formset_class = MerchandiseFormset
    inlinescolor_class = MerchandiseColorFormset
    inlinessize_class = MerchandiseSizeFormset
    inlinesfile_class = MerchandisefileFormset
    template_name = "crud/merchandise/update/merchandiseformupdate.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        #イメージファイル
        pk = self.kwargs.get("pk")
        profile = MerchandiseFileUpload.objects.filter(McdDtuploadid=pk,is_Deleted=0)
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['merchandisepageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(MerchandiseUpdateView, self).get_context_data(**kwargs)
        context.update(dict(formset=MerchandiseFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseDetail.objects.filter(is_Deleted=0))),
                       inlinescolor=MerchandiseColorFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseColor.objects.filter(is_Deleted=0)),
                       inlinessize=MerchandiseSizeFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseSize.objects.filter(is_Deleted=0)),
                       inlinesfile=MerchandisefileFormset(self.request.POST or None, files=self.request.FILES or None, instance=self.get_object(), queryset=MerchandiseFileUpload.objects.filter(McdDtuploadid=pk,is_Deleted=0)),
                       images=profile,
                       row=param,
                       previewurl=self.request.session['merchandisepageno'],
                    )

        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    def form_valid(self, form):
        try:
            post = form.save(commit=False)
            formset = MerchandiseFormset(self.request.POST,instance=post) 
            inlinescolor = MerchandiseColorFormset(self.request.POST,instance=post)
            inlinessize = MerchandiseSizeFormset(self.request.POST,instance=post)
            inlinesfile = MerchandisefileFormset(self.request.POST, files=self.request.FILES, instance=post)

            if self.request.method == 'POST' and formset.is_valid() and inlinescolor.is_valid() and inlinessize.is_valid():
                instances = formset.save(commit=False)
                instancecolor = inlinescolor.save(commit=False)
                instancesize = inlinessize.save(commit=False)
                #アップロードファイルの存在確認
                if inlinesfile.files!={}:
                    if inlinesfile.errors:
                        for errmessage in inlinesfile.errors:
                            if errmessage:
                                message = errmessage
                                logger.error(message)
                                messages.error(self.request,message) 

                                return self.render_to_response(self.get_context_data(form=form, formset=formset, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile,))
                    instancefile = inlinesfile.save(commit=False)
            
                if form.is_valid():
                    # Updated_idフィールドはログインしているユーザidとする
                    post.Updated_id = self.request.user.id
                    # Updated_atは現在日付時刻とする
                    post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時               
                    post.save()

                if formset.is_valid():
                    # 削除チェックがついたfileを取り出して更新
                    for file in formset.deleted_objects:
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.is_Deleted = True
                        file.save()

                    # 明細のfileを取り出して更新
                    for file in instances:
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.save()

                if inlinescolor.is_valid():
                    # カラー明細の削除チェックがついたfileを取り出して更新
                    for file in inlinescolor.deleted_objects:
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.is_Deleted = True
                        file.save()

                    for file in instancecolor:
                        file.Created_id = self.request.user.id
                        file.Updated_id = self.request.user.id
                        file.save()

                if inlinessize.is_valid():
                    # サイズ明細の削除チェックがついたfileを取り出して更新
                    for file in inlinessize.deleted_objects:
                        file.Updated_id = self.request.user.id
                        file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                        file.is_Deleted = True
                        file.save()

                    for file in instancesize:
                        file.Created_id = self.request.user.id
                        file.Updated_id = self.request.user.id
                        file.save()

                if inlinesfile.files !={}:
                    if inlinesfile.is_valid():
                        # アップロードファイルの削除チェックがついたfileを取り出して更新
                        for file in inlinesfile.deleted_objects:
                            file.Updated_id = self.request.user.id
                            file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                            file.is_Deleted = True
                            file.save()

                        for file in instancefile:
                            file.Created_id = self.request.user.id
                            file.Updated_id = self.request.user.id
                            file.save()
            else:
                message = "エラーが発生しました"
                logger.error(message)
                messages.error(self.request,message) 
                incoming_url = self.request.session['merchandisepageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

                return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile))

            if 'merchandisepageno' in self.request.session:
                incoming_url = self.request.session['merchandisepageno']
                param=self.request.POST.get('row')
                #listViewに戻るURLを取得
                url = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return redirect(url)
        except Exception as e:
            message = "更新エラーが発生しました"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.META['merchandisepageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile))
    # バリデーションエラー時
    def form_invalid(self,form):
        message = "更新エラーが発生しました"
        logger.error(message)
        messages.error(self.request,message) 
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['merchandisepageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=self.inlinescolor_class, inlinessize=self.inlinessize_class, inlinesfile=self.inlinesfile_class))

# 商品情報削除
class MerchandiseDeleteView(LoginRequiredMixin,UpdateView):
    model = Merchandise
    form_class =  MerchandiseForm
    formset_class = MerchandiseFormset
    inlinescolor_class = MerchandiseColorFormset
    inlinessize_class = MerchandiseSizeFormset
    inlinesfile_class = MerchandisefileFormset
    template_name = "crud/merchandise/delete/merchandiseformdelete.html"

    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        #イメージファイル
        pk = self.kwargs.get("pk")
        #templateページのrowを取得
        param = self.kwargs.get('row')
        #ListViewに戻るときに色を付加する
        incoming_url = self.request.META['HTTP_REFERER']
        #listViewに戻るURLを取得
        self.request.session['merchandisepageno'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        context = super(MerchandiseDeleteView, self).get_context_data(**kwargs)
        context.update(dict(formset=MerchandiseFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseDetail.objects.filter(is_Deleted=0))),
                       inlinescolor=MerchandiseColorFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseColor.objects.filter(is_Deleted=0)),
                       inlinessize=MerchandiseSizeFormset(self.request.POST or None, instance=self.get_object(), queryset=MerchandiseSize.objects.filter(is_Deleted=0)),
                       inlinesfile=MerchandisefileFormset(self.request.POST or None, files=self.request.FILES or None, instance=self.get_object(), queryset=MerchandiseFileUpload.objects.filter(McdDtuploadid=pk,is_Deleted=0)),
                       row=param,
                       previewurl=self.request.session['merchandisepageno'],
                       )      
       
        return context

    # form_valid関数をオーバーライドすることで、更新するフィールドと値を指定できる
    @transaction.atomic # トランザクション設定
    def form_valid(self, form):
        post = form.save(commit=False)
        formset = MerchandiseFormset(self.request.POST,instance=post) 
        inlinescolor = MerchandiseColorFormset(self.request.POST,instance=post)
        inlinessize = MerchandiseSizeFormset(self.request.POST,instance=post)
        inlinesfile = MerchandisefileFormset(self.request.POST,self.request.FILES,instance=post)

        pk = self.kwargs.get("pk")
        ReqCnt = ProductOrder.objects.filter(is_Deleted=0,ProductOrderMerchandiseCode=pk).count()
        if ReqCnt > 0:
            message = "製品発注が存在するため削除できません。製品発注を削除してください。"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['merchandisepageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile))

        if self.request.method == 'POST':
            instances = formset.save(commit=False)
            instancecolor = inlinescolor.save(commit=False)
            instancesize = inlinessize.save(commit=False)
          
            if form.is_valid():
                post.is_Deleted = True
                # Updated_idフィールドはログインしているユーザidとする
                post.Updated_id = self.request.user.id
                # Updated_atは現在日付時刻とする
                post.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時               
                post.save()

            if formset.is_valid():
                # 明細のfileを取り出して削除フラグ更新
                for file in instances:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()

            if inlinescolor.is_valid():
                # カラー明細のfileを取り出して削除フラグ更新
                for file in instancecolor:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()

            if inlinessize.is_valid():
                # サイズ明細のfileを取り出して削除フラグ更新
                for file in instancesize:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()

            if inlinesfile.is_valid():
                # アップロードファイルの削除チェックがついたfileを取り出して更新
                instancefile = inlinesfile.save(commit=False)
                for file in instancefile:
                    file.is_Deleted = True
                    file.Updated_id = self.request.user.id
                    file.Updated_at = timezone.now() + datetime.timedelta(hours=9) # 現在の日時
                    file.save()
        else:
            message = "削除できませんでした"
            logger.error(message)
            messages.error(self.request,message) 
            #ListViewに戻るときに色を付加する
            incoming_url = self.request.session['merchandisepageno']
            param=self.request.POST.get('row')
            #listViewに戻るURLを取得
            self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

            return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=inlinescolor, inlinessize=inlinessize, inlinesfile=inlinesfile))

        if 'merchandisepageno' in self.request.session:
            incoming_url = self.request.session['merchandisepageno']
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
        incoming_url = self.request.session['merchandisepageno']
        param=self.request.POST.get('row')
        #listViewに戻るURLを取得
        self.request.META['HTTP_REFERER'] = viewsGetUrlFunction.GetUrl(param, incoming_url)

        return self.render_to_response(self.get_context_data(form=form, formset=self.formset_class, inlinescolor=self.inlinescolor_class, inlinessize=self.inlinessize_class, inlinesfile=self.inlinesfile_class))
