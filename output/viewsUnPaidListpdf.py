from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape  
from myapp.models import RequestResult, CustomerSupplier
from myapp.output import unpaidfunction
# 検索機能のために追加
from django.db.models import Q, Max
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce
from itertools import chain
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request, TargetMonth, element):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "UnPaidList_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = conversion(TargetMonth)
        result = make(search_date, element, response)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:unpaidlist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:unpaidlist")
    return response

def make(search_date, element, response):
    pdf_canvas = set_info(response) # キャンバス名

    if element=='0':
        dt_customer = customerAll(search_date)
    else:
        dt_customer = customer(search_date,element)

    counter = len(dt_customer)

    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt_Detail = Detail(search_date, dt_customer[i]['Supplier_max'])
        result=unpaidfunction.printstring(pdf_canvas, dt_Detail, search_date[4])

    pdf_canvas.save() # 保存

    return result

def conversion(TargetMonth):
    # 月初、月末を算出する
    tdate = datetime.datetime.strptime(str(TargetMonth), '%Y%m%d')
    startdate = tdate + relativedelta.relativedelta(day=1)
    lastdate = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)

    # 前月初日、末日を算出する
    Prvstartdate = tdate + relativedelta.relativedelta(months=-1,day=1)
    Prvlastdate = tdate + relativedelta.relativedelta(day=1,days=-1)
    PrtDate = tdate + relativedelta.relativedelta(day=1)

    # 月初
    startdate = startdate.strftime('%Y-%m-%d')
    # 月末
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 前月初日
    Prvstartdate = Prvstartdate.strftime('%Y-%m-%d')
    # 前月末日
    Prvlastdate = Prvlastdate.strftime('%Y-%m-%d')

    #印刷用年月
    PrtDate = PrtDate.strftime('%Y年%m月')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, PrtDate)

#未払一覧表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("未払一覧表")
    pdf_canvas.setSubject("未払一覧表")
    return pdf_canvas

def customerAll(search_date):
    queryset =  list(RequestResult.objects.values(
        'OrderingId__SupplierCode_id__CustomerCode',
        ).filter(
            PaymentInputDiv=False, 
            InvoiceIssueDate__lte=str(search_date[1]),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
        ).annotate(
            Supplier_max=Max('OrderingId__SupplierCode_id__CustomerCode')
            ))

    return queryset

def customer(search_date, element):
    queryset =  list(RequestResult.objects.values(
        'OrderingId__SupplierCode_id__CustomerCode',
        ).filter(
            PaymentInputDiv=False, 
            InvoiceIssueDate__lte=str(search_date[1]),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
        ).annotate(
            Supplier_max=Max('OrderingId__SupplierCode_id__CustomerCode')
            ).filter(
                OrderingId__SupplierCode_id__id=str(element)
            )
        )

    return queryset

def Detail(search_date, Customer):
    queryset =  RequestResult.objects.values(
        'InvoiceIssueDate',
        'OrderingId__SupplierCode_id__CustomerCode',
        'OrderingId__SupplierCode_id__CustomerName',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        'SlipNumber',
        'OrderingId__ProductName',
        'OrderingId__OrderingCount',
        'OrderingDetailId__DetailVolume',
        'OrderingDetailId__DetailUnitPrice',
        'OrderingDetailId__DetailSummary',
        ).annotate(
            Supplier_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()
        )).filter(
            PaymentInputDiv=False, 
            InvoiceIssueDate__lte=str(search_date[1]),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            OrderingId__SupplierCode_id__CustomerCode=str(Customer),
            ).order_by(
                'OrderingId__SupplierCode_id__CustomerCode',
                'InvoiceIssueDate',
                'ShippingDate',
                )
    result=(list(queryset))

    return result

if __name__ == '__main__':
    make()   
