from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from myapp.models import Deposit, CustomerSupplier, RequestResult
from myapp.output import invoicefunction

# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from django.db.models import Sum,F,DecimalField
from django.db.models.functions import Coalesce
from itertools import chain

# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request, pkclosing, invoiceDate_From, invoiceDate_To, element_From, element_To):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "Invoice_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)

        # 文字列を日付に変換する
        search_date = conversion(invoiceDate_From, invoiceDate_To, pkclosing)
        result = make(pkclosing, search_date[0], search_date[1], element_From, element_To, search_date[2], search_date[3],response, request)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:invoicelist")
    if result==99:
        message = "請求書発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:invoicelist")
    return response

def make(closing, invoiceDate_From, invoiceDate_To, element_From, element_To, lastdate, billdate, response, request):
    pdf_canvas = set_info(response) # キャンバス名
    dt_own = Own_Company()
    dt_company = company(closing, element_From, element_To)
    counter = len(dt_company)
    PrCnt=0
    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt = customer(i, dt_company)
        dt_Prev = PrevBalance(lastdate, dt, invoiceDate_From, invoiceDate_To)
        dt_Detail = Detail(dt, invoiceDate_From, invoiceDate_To)

        if dt_Prev[5]!=0 or dt_Prev[1]!=0:
            print_string(pdf_canvas, dt_own, dt, billdate, dt_Prev, dt_Detail, invoiceDate_From)
            result=0
            PrCnt=1
    if PrCnt!=0:
        pdf_canvas.save() # 保存
    else:
        result=99
        
    return result

def conversion(invoiceDate_From, invoiceDate_To, pkclosing):
    # 前月同日を算出する
    if pkclosing==31:
        tdate = datetime.datetime.strptime(str(invoiceDate_From), '%Y%m%d')
        lastdate = tdate - relativedelta.relativedelta(days=1)
    else:
        tdate = datetime.datetime.strptime(str(invoiceDate_To), '%Y%m%d')
        lastdate = tdate - relativedelta.relativedelta(months=1)

    # 文字列を日付に変換する
    invoiceDate_From = datetime.datetime.strptime(str(invoiceDate_From), '%Y%m%d') 
    invoiceDate_To = datetime.datetime.strptime(str(invoiceDate_To), '%Y%m%d')

    # 日付型に変換する
    # 前月同日
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 日付範囲指定From
    Date_From = invoiceDate_From.strftime('%Y-%m-%d') 
    # 日付範囲指定To
    Date_To = invoiceDate_To.strftime('%Y-%m-%d') 
    # 請求日
    billdate = invoiceDate_To.strftime('%Y年%m月%d日')
    return(Date_From, Date_To, lastdate, billdate)

#一括請求書
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("一括請求書")
    pdf_canvas.setSubject("一括請求書")
    return pdf_canvas

def Own_Company():
    queryset = CustomerSupplier.objects.filter(CustomerCode=('A0042'))
    Own_Company = list(queryset.values(
                                    'CustomerCode',
                                    'CustomerName',
                                    'PostCode',
                                    'PrefecturesCode__prefecturename',
                                    'Municipalities',
                                    'Address',
                                    'BuildingName',
                                    'PhoneNumber',
                                    'FaxNumber',
                                ))

    return Own_Company

def company(closing, element_From, element_To):
    queryset = CustomerSupplier.objects.filter(id__range=(element_From,element_To),ClosingDate=(closing),is_Deleted=0).order_by('CustomerCode')
    Company = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'Department',
                                    'PostCode',
                                    'PrefecturesCode__prefecturename',
                                    'Municipalities',
                                    'Address',
                                    'BuildingName',
                                    'ClosingDate',
                                    'LastClaimBalance',
                            ))

    return Company

def customer(i, dt_company):
    queryset = CustomerSupplier.objects.filter(CustomerCode=(str(dt_company[i]['CustomerCode'])),is_Deleted=0)
    Customer = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'Department',
                                    'PostCode',
                                    'PrefecturesCode__prefecturename',
                                    'Municipalities',
                                    'Address',
                                    'BuildingName',
                                    'ClosingDate',
                                    'LastClaimBalance',
                            ))

    return Customer

def PrevBalance(lastdate, Customer, FromDate, ToDate): 
    #前月までの入金額計
    queryset = Deposit.objects.filter(DepositDate__lte=(str(lastdate)),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    DepoPrvSum = list(queryset.values('DepositCustomerCode').annotate(Depo_total=Coalesce(Sum('DepositMoney'),0,output_field=DecimalField())))
    #0判定
    if DepoPrvSum:
        DepoPrvTotal = int(DepoPrvSum[0]['Depo_total'])
    else:
        DepoPrvTotal = 0
    #前月までの売上額計
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__lte=(str(lastdate)),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )
    SellPrvSum =  list(queryset.values('OrderingId__CustomeCode').annotate(
        Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=DecimalField())))
    #0判定
    if SellPrvSum:
        SellPrvTotal = int(SellPrvSum[0]['Abs_total'])
        SellPrvtax = int(SellPrvSum[0]['Abs_total']) * 0.1
        SellPrvtax = int(SellPrvtax)
    else:
        SellPrvTotal = 0
        SellPrvtax = 0
    #前回請求額算出
    PrevBill = int(Customer[0]['LastClaimBalance']) - int(DepoPrvTotal) + int(SellPrvTotal) + int(SellPrvtax)
    #請求月入金合計額
    queryset = Deposit.objects.filter(DepositDate__range=(str(FromDate),str(ToDate)),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    DepoSum = list(queryset.values('DepositCustomerCode').annotate(Depo_total=Coalesce(Sum('DepositMoney'),0,output_field=DecimalField())))
    #0判定
    if DepoSum:
        DepoTotal = int(DepoSum[0]['Depo_total'])
    else:
        DepoTotal = 0
    #繰越額
    CarryForward = int(PrevBill) - int(DepoTotal)   
    #請求月売上合計額
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(FromDate),str(ToDate)),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )

    SellSum =  list(queryset.values('OrderingId__CustomeCode').annotate(
        Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=DecimalField())))
    #0判定
    if SellSum:
        SellTotal = int(SellSum[0]['Abs_total'])
    else:
        SellTotal = 0
    #請求月売上消費税額
    tax = int(SellTotal) * 0.1
    tax = int(tax)
    #今回請求額
    invoice = int(CarryForward) + int(SellTotal) + int(tax)
    return(PrevBill, DepoTotal, CarryForward, SellTotal, tax, invoice)

def Detail(Customer, FromDate, ToDate ): 
    #請求月売上レコード
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(FromDate),str(ToDate)),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )
    queryset =  queryset.values('InvoiceNUmber','OrderingId__CustomeCode','OrderingId__SlipDiv','OrderingId__OrderNumber',
                                'OrderingId__CustomeCode_id__CustomerName','OrderingId__ProductName','OrderingId__OrderingCount',
                                'InvoiceIssueDate','SalesTaxRate').annotate(
                                    Abs_total=Sum(F("ShippingVolume") * F("OrderingDetailId__DetailSellPrice")),
                                    Shipping_total=Sum('ShippingVolume')
                                    ).order_by(
                                        'InvoiceIssueDate',
                                        'InvoiceNUmber'
                                    )
    queryset =  queryset.values_list(
         'InvoiceIssueDate',
         'InvoiceNUmber',
         'OrderingId__ProductName',
         'OrderingId__OrderingCount',
         'Shipping_total',
         'Abs_total',
         'SalesTaxRate',
        ).filter(Abs_total__gt=0)

    #請求月入金レコード
    queryset_depo = Deposit.objects.filter(DepositDate__range=(str(FromDate),str(ToDate)),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset_depo = queryset_depo.values_list('DepositDate','DepositSummary','DepositDiv__DepoPayDivname','DepositSummary','DepositSummary','DepositMoney','DepositDiv_id')

    #繰越レコードと売上レコードと入金レコードを結合
    #result = list(chain(queryset, queryset_depo))
    obj = chain(queryset, queryset_depo)
    #日付順にソート
    result = sorted(obj)

    return result
#一括請求書発行
def print_string(pdf_canvas, dt_own, dt, billdate, dt_Prev, dt_Detail, Date_From):
    invoicefunction.printstring(pdf_canvas, dt_own, dt, billdate, dt_Prev, dt_Detail, Date_From)

if __name__ == '__main__':
    make()   