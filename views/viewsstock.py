from django.shortcuts import render, redirect
from django.views.generic import ListView 
from myapp.models import CustomerSupplier
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.form.formsstock import StockForm
from myapp.output import stockextractfunction, stockexceloutputfunction, viewsGetDateFunction
from django.contrib.auth import get_user_model
# 日時
from django.utils import timezone
from dateutil import relativedelta
# ajax
from django.http import JsonResponse

# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class StockManageView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    form_class =  StockForm
    template_name = "crud/stock/list/stocklist.html"

    def get_context_data(self, **kwargs):
        context = super(StockManageView, self).get_context_data(**kwargs)
        context.update(GetMonth=timezone.now().date() + relativedelta.relativedelta(months=-1))
        context.update(Manager=get_user_model().objects.values('id','first_name', 'last_name'))

        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset

    def List(request):
        try:
            TargetMonth = request.GET.get('Target', None)
            search_date = viewsGetDateFunction.conversion(TargetMonth)
            OrderNumber = request.GET.getlist('row', None)       
            # データ抽出
            Datatable = stockextractfunction.treatment(search_date, OrderNumber)
        except Exception as e:
            message = "在庫データ抽出時にエラーが発生しました"
            logger.error(message)
            messages.add_message(request, messages.ERROR, message)
            return redirect("myapp:stock")

        # listに変換
        Datatable=list(Datatable)

        context = {
            'form': Datatable,
        }

        context.update(GetMonth=timezone.now().date() + relativedelta.relativedelta(months=-1))
        context.update(StartDate=str(search_date[0]))
        context.update(EndDate=str(search_date[1]))

        return render(request, 'crud/stock/list/stocklist.html', context) 

    def ajax_result(request):
        if request.method == 'GET':  # GETの処理
            table_param = request.GET.get("Order")          # GETパラメータ(オーダーNO)
            Start_date = request.GET.get("Stdt")            # GETパラメータ(開始日)
            End_date = request.GET.get("Eddt")              # GETパラメータ(終了日)
            DuPrice = request.GET.get("DuPrice")            # GETパラメータ(仕入単価)
            PrPrice = request.GET.get("PrPrice")            # GETパラメータ(加工単価)
            Item = request.GET.get("Item")                  # GETパラメータ(項番)

            try:
                CarryForward_Record = stockextractfunction.carryforward(table_param, Start_date, End_date, DuPrice, PrPrice, Item)
            except Exception as e:
                return redirect("myapp:stocklist")

            detail=list(CarryForward_Record)
      
            context = {
                'list': detail,
            }

            return JsonResponse(context)

    def excel_output(request):
        TargetMonth = request.GET.get('Target', None)
        search_date = viewsGetDateFunction.conversion(TargetMonth)
        OrderNumber = ""
        # データ抽出
        table=stockextractfunction.treatment(search_date, OrderNumber)

        # listに変換
        table=list(table)

        # 件数確認
        if len(table)==0:
            message = "抽出データありません"
            logger.error(message)
            messages.add_message(request, messages.WARNING, message)
            return redirect("myapp:stocklist")
        try:
            response = stockexceloutputfunction.exceloutput(request, table, search_date)
        except Exception as e:
            message = "Excel作成時にエラーが発生しました"
            logger.error(message)
            messages.add_message(request, messages.ERROR, message)
            return redirect("myapp:stocklist")

        # 生成したHttpResponseをreturnする
        return response