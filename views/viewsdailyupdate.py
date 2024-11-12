from django.shortcuts import render,redirect
from django.views.generic import ListView, CreateView
from myapp.models import InvoiceNo,RequestResult
from myapp.form.formsdailyupdate import DailyUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
# 計算用
from decimal import Decimal
# LOG出力設定
import logging
logger = logging.getLogger(__name__)
#Pagenation
from django.core.paginator import Page

# 個別請求情報一覧/検索
class DailyUpdateListView(LoginRequiredMixin,ListView):
    model = RequestResult
    paginate_by = 20
    template_name = "crud/dailyupdate/dailyupdate.html"
    queryset = RequestResult.objects.filter(DailyUpdateDiv=False,is_Deleted=0).order_by('ShippingDate').reverse()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pagination
        page: Page = context["page_obj"]
        # get_elided_page_rangeの結果を、paginator_range変数から使用可能
        context["paginator_range"] = page.paginator.get_elided_page_range(
                                                           page.number,
                                                           on_each_side=2,
                                                           on_ends=1)
        return context

class DailyUpdateView(LoginRequiredMixin,CreateView):
    model = InvoiceNo
    form_class =  DailyUpdateForm
    template_name = "crud/dailyupdate/dailyupdate.html"

    def form_valid(self, form):
        if self.request.method == "POST":
            if form.is_valid():
                try:       
                    DailyDate = form.data.get('DailyUpdateDate')

                    dt = extract(DailyDate) 
                    length=len(dt)

                    if length == 0:
                        message = "更新対象データがありませんでした"
                        logger.error(message)
                        messages.add_message(self.request, messages.WARNING, message)

                        return redirect("myapp:DailyUpdate")
                    userid = self.request.user.id
                    OrderNumber = ''
                    for i in range(length):
                        updid = dt[i]['id']
                        SlipDiv = dt[i]['OrderingId__SlipDiv']
                        invdt = getInvoiceNo()
                        InvNo = invdt[0]['InvoiceNo']

                        if (OrderNumber != str(dt[i]['OrderingId__SlipDiv'] + dt[i]['OrderingId__OrderNumber'])) or \
                            (OrderNumber == str(dt[i]['OrderingId__SlipDiv'] + dt[i]['OrderingId__OrderNumber']) and \
                             CustomerCode != str(dt[i]['OrderingId__CustomeCode'])):

                            InvNo += Decimal(1)

                        UpdateRequestResult(updid,DailyDate,InvNo,userid)
                        UpdateInvoiceNo(InvNo,userid,SlipDiv)
                        OrderNumber = str(dt[i]['OrderingId__SlipDiv'] + dt[i]['OrderingId__OrderNumber'])
                        CustomerCode = str(dt[i]['OrderingId__CustomeCode'])
                except Exception as e:
                    message = "日次更新時にエラーが発生しました"
                    logger.error(message)
                    messages.add_message(self.request, messages.ERROR, message)

                    return redirect("myapp:DailyUpdate")

            message = "日次更新処理正常終了"
            logger.error(message)
            messages.add_message(self.request, messages.SUCCESS, message)

            return redirect('myapp:DailyUpdatelist')

def extract(DailyDate):
    queryset =  list(RequestResult.objects.values(
        'id',
        'InvoiceIssueDiv',
        'DailyUpdateDiv',
        'DailyUpdateDate',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        'OrderingId__CustomeCode'
        ).filter(
            DailyUpdateDiv=False, 
            DailyUpdateDate__lte=(str(DailyDate)),
            is_Deleted=0,
                ))

    return queryset

def getInvoiceNo():
    queryset =  InvoiceNo.objects.values(
        'InvoiceNo',
        'SInvoiceNo'
    ).filter(
        id=1
    )

    return queryset

def UpdateRequestResult(pk,DailyUpdate,InvNo,userid):
    #RequestResultテーブル更新処理
    result = RequestResult.objects.filter(
        id=str(pk)
        ).update(
            InvoiceNUmber=str(InvNo),
            DailyUpdateDiv=True,
            DailyUpdateDate=str(DailyUpdate),
            Updated_id=str(userid),
            Updated_at = timezone.now() + datetime.timedelta(hours=9)
            )

    return result

def UpdateInvoiceNo(InvNo,userid,SlipDiv):
    #InvoiceNoテーブル更新処理
    result = InvoiceNo.objects.filter(
        id=1
        ).update(
            InvoiceNo=str(InvNo),
            Updated_id=str(userid),
            Updated_at = timezone.now() + datetime.timedelta(hours=9),
            )

    return result