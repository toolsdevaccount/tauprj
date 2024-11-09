from django.shortcuts import render, HttpResponse
from myapp.models import RequestResult,CustomerSupplier
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
# Transaction
from django.db import transaction
# models
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce
from dateutil import relativedelta
# ajax
from django.http import JsonResponse
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

class UnPaidListView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    template_name = "crud/unpaid/unpaidformupdate.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(CustomerCode_From = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_To = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').filter(is_Deleted=0),)
        context.update(CustomerCode_Max = CustomerSupplier.objects.values('id','CustomerCode','CustomerOmitName').order_by('id').reverse().filter(is_Deleted=0).first())
    
        return context
    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset
    def List(request,TargetMonth):
        search_date = conversion(TargetMonth)
        queryset =  RequestResult.objects.values(
            'id',
            'OrderingId__SupplierCode_id__CustomerCode',
            'OrderingId__SupplierCode_id__CustomerName',
            'OrderingId__ProductName',
            'OrderingId__OrderingCount',
            'OrderingDetailId__DetailColorNumber',
            'OrderingDetailId__DetailColor',
            'InvoiceIssueDate',
            'ShippingDate',
            'PaymentInputDiv',
            'SlipNumber',
            ).annotate(
                Supplier_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()
            )).filter(
                PaymentInputDiv=False, 
                InvoiceIssueDate__lte=str(search_date[1]),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                ResultMoveDiv=0,
                    ).order_by(
                        'OrderingId__SupplierCode_id__CustomerCode',
                        'InvoiceIssueDate',
                        'ShippingDate',
                    )
        context = {
            'form': queryset,
        }

        return render(request, 'crud/unpaid/unpaidformupdate.html', context)

    @transaction.atomic # トランザクション設定
    def update(request):
        if request.method == 'POST':
            i=0
            leng=request.POST.get("counter")
            leng=int(leng)+1

            try:
                for i in range(leng):
                    pk=request.POST.get("form-" + str(i) + "-id")
                    Updated_at = timezone.now() + datetime.timedelta(hours=9)
                    User = request.user.id
                    #支払済区分
                    input_PaymentInputDiv = request.POST.get("form-" + str(i) + "-PaymentInputDiv")
                    if input_PaymentInputDiv==None:
                        input_PaymentInputDiv='False'
                    else:
                        input_PaymentInputDiv='True'
                    RequestResult.objects.update_or_create(
                        pk=pk, 
                        defaults={
                            "PaymentInputDiv":input_PaymentInputDiv,
                            "Updated_at":Updated_at,
                            "Updated_id":User,
                            })
                message = "更新が正常に終了しました"
                #ListViewに戻るときに色を付加する
                dict = {
                        "answer": message,
                        }

                return JsonResponse(dict)
            except Exception as e:
                # is_validがFalseの場合はエラー文を表示
                message = "更新エラーが発生しました.\n入力値を確認してください."
                logger.error(message)
                #ListViewに戻るときに色を付加する
                return HttpResponse(message, status=400, content_type='application/json')

def conversion(TargetMonth):
    # 月初、月末を算出する
    tdate = datetime.datetime.strptime(str(TargetMonth), '%Y%m%d')
    startdate = tdate + relativedelta.relativedelta(day=1)
    lastdate = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)
    # 月初、月末を算出する(YYYY年mm月dd日用)
    strstart = tdate + relativedelta.relativedelta(day=1)
    strlast = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)

    # 前月初日、末日を算出する
    Prvstartdate = tdate + relativedelta.relativedelta(months=-1,day=1)
    Prvlastdate = tdate + relativedelta.relativedelta(day=1,days=-1)

    # 月初
    startdate = startdate.strftime('%Y-%m-%d')
    # 月末
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 月初(YYYY年mm月dd日用)
    strstart = strstart.strftime('%Y年%m月%d日')
    # 月末(YYYY年mm月dd日用)
    strlast = strlast.strftime('%Y年%m月%d日')
    # 前月初日
    Prvstartdate = Prvstartdate.strftime('%Y-%m-%d')
    # 前月末日
    Prvlastdate = Prvlastdate.strftime('%Y-%m-%d')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, strstart, strlast)
