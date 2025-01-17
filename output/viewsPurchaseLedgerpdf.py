from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B4, landscape  
from myapp.models import Payment, CustomerSupplier, RequestResult
from myapp.output import purchaseLedgerfunction
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
from django.db.models.functions import TruncMonth
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request, TargetMonth, element_From, element_To):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "PurchaseLedger_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = conversion(TargetMonth)
        result = make(search_date, element_From, element_To, response)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:PurchaseLedgerlist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:PurchaseLedgerlist")
    return response

def make(search_date, element_From, element_To, response):
    pdf_canvas = set_info(response) # キャンバス名
    dt_company = company(element_From, element_To)
    counter = len(dt_company)
    PrCnt=0

    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt = customer(i, dt_company)
        dt_Prev = PrevBalance(search_date, dt)
        dt_Detail = Detail(search_date, dt)

        if dt_Prev[0]!=0 or dt_Prev[6]!=0:
            purchaseLedgerfunction.printstring(pdf_canvas, dt, dt_Prev, dt_Detail, search_date[4], search_date[5])
            result=0
            PrCnt=1

    if PrCnt!=0:
        pdf_canvas.save() # 保存
    else:
        result=99

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
    PrintDate = PrtDate.strftime('%Y年%m月')

    #繰越年月日
    CurryDate = PrtDate.strftime('%Y/%m/%d')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, PrintDate, CurryDate)

#仕入台帳
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("仕入台帳")
    pdf_canvas.setSubject("仕入台帳")
    return pdf_canvas

def company(element_From, element_To):
    queryset = CustomerSupplier.objects.filter(is_Deleted=0)
    Company = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'ClosingDate',
                                    'LastPayable',
                            ).filter(Q(MasterDiv=3) | Q(MasterDiv=4),id__gte=element_From,id__lte=element_To).order_by('CustomerCode'))

    return Company

def customer(i, dt_company):
    queryset = CustomerSupplier.objects.filter(CustomerCode=(str(dt_company[i]['CustomerCode'])),is_Deleted=0)
    Customer = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'ClosingDate',
                                    'LastPayable',
                            ))

    return Customer

def PrevBalance(search_date, Customer): 
    #前月までの支払額計
    queryset = Payment.objects.filter(PaymentDate__lte=(str(search_date[3])),PaymentSupplierCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset = queryset.filter(~Q(PaymentDiv=11))

    PayPrvSum = list(queryset.values('PaymentSupplierCode').annotate(Pay_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())))
    #0判定
    if PayPrvSum:
        PayPrvTotal = int(PayPrvSum[0]['Pay_total'])
    else:
        PayPrvTotal = 0

    #前月までの仕入額計
    StockPrvSum =  RequestResult.objects.annotate(
        monthly=TruncMonth('InvoiceIssueDate')
        ).values(
            'monthly',
            'id',
        ).filter(
            InvoiceIssueDate__lte=(str(search_date[3])),
            OrderingId__SupplierCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            ).annotate(
                    Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()),
                ).order_by(
                    'monthly'
                )
    
    #消費税調整抽出
    Adjustment = Payment.objects.values(
        'PaymentSupplierCode'
        ).annotate(
            Adjustment_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
            ).filter(
                 PaymentDate__lte=(str(search_date[3]))
                ,PaymentSupplierCode=(str(Customer[0]['id']))
                ,is_Deleted=0
                ,PaymentDiv=11
                )

    #0判定
    if Adjustment:
        AdjustmentTotal = int(Adjustment[0]['Adjustment_total'])
    else:
        AdjustmentTotal = 0

    #残高消費税計算
    tax=0
    StockPrvTotal=0
    Stocktax=0
    StockPrvtax=0
    monthly=0
    dcnt = len(StockPrvSum)
    if StockPrvSum:
        for i,q in  enumerate(StockPrvSum):
            if (i!=0 and monthly!=q['monthly']) or i==dcnt-1:
                if i==dcnt-1:
                    tax+= int(q['Abs_total'])
                Stocktax=int(tax*0.1)
                StockPrvtax+=Stocktax
                tax=0
            StockPrvTotal+=int(q['Abs_total'])
            tax+= int(q['Abs_total'])

            monthly=q['monthly']

        StockPrvtax+= int(AdjustmentTotal)

    #前回買掛額算出
    PrevBill = int(Customer[0]['LastPayable']) - int(PayPrvTotal) + int(StockPrvTotal) + int(StockPrvtax)
    #当月支払合計額
    queryset = Payment.objects.filter(PaymentDate__range=(str(search_date[0]),str(search_date[1])),PaymentSupplierCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset = queryset.filter(~Q(PaymentDiv=11))

    PaySum = list(queryset.values('PaymentSupplierCode').annotate(Pay_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())))
    #0判定
    if PaySum:
        PayTotal = int(PaySum[0]['Pay_total'])
    else:
        PayTotal = 0
    #買掛金繰越額
    CarryForward = int(PrevBill) - int(PayTotal)   

    #当月支払消費税調整額
    Adjustment = Payment.objects.values('PaymentSupplierCode').annotate(
                                        Adjustment_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
                                        ).filter(
                                             PaymentDate__range=(str(search_date[0]),str(search_date[1]))
                                            ,PaymentSupplierCode=(str(Customer[0]['id']))
                                            ,is_Deleted=0
                                            ,PaymentDiv=11
                                            )
    Adjustment = list(Adjustment.values('Adjustment_total'))
    #0判定
    if Adjustment:
        AdjustmentTotal = int(Adjustment[0]['Adjustment_total'])
    else:
        AdjustmentTotal = 0

    #当月仕入合計額
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__SupplierCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )

    StockSum =  list(queryset.values(
        'OrderingId__SupplierCode',
        'id',
        'InvoiceNUmber'
        ).annotate(
            Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()))
            )

    StockTotal = 0
    for d in StockSum:
        StockTotal+=int(d['Abs_total'])

    #当月仕入消費税額
    tax = int(StockTotal) * 0.1 + int(AdjustmentTotal)
    tax = int(tax)

    #当月税込仕入合計額
    invoice = int(CarryForward) + int(StockTotal) + int(tax)
    CarryOver = int(PrevBill) + int(invoice) - int(PayTotal)

    return(PrevBill, PayTotal, CarryForward, StockTotal, tax, invoice, CarryOver)

def Detail(search_date, Customer): 
    #請求月仕入レコード
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__SupplierCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                OrderingDetailId__DetailUnitPrice__gt=0,
                )
    queryset =  queryset.values(
        'SlipNumber',
        'OrderingId__SupplierCode', 
        'OrderingDetailId__DetailUnitPrice',
        'id',
        ).annotate(
            Abs_total=Sum(F('ShippingVolume') * F('OrderingDetailId__DetailUnitPrice')),
            Shipping_total=Sum('ShippingVolume'),
            ResultDate_Max=Max('ResultDate'),
            ProductName_Max=Max('OrderingId__ProductName'),
            OrderingCount_Max=Max('OrderingId__OrderingCount'),
            SlipDiv_Max=Max('OrderingId__SlipDiv'),
            OrderNumber_Max=Max('OrderingId__OrderNumber'),
            SlipNumber_Max=Max('SlipNumber'),
            ShippingVolume_Max=Max('ShippingVolume'),
            DetailUnitPrice_Max=Max('OrderingDetailId__DetailUnitPrice'),
            ShippingDate_Max=Max('ShippingDate'),
            InvoiceIssueDate_Max=Max('InvoiceIssueDate'),
            ).order_by(
                'InvoiceIssueDate',
                'ShippingDate',
                'SlipNumber'
                )

    queryset = list(queryset)
    stock_list = []
    if queryset:
        for i in queryset:
            stock = {
                'InvoiceIssueDate': i["InvoiceIssueDate_Max"],
                'SlipNumber':i["SlipNumber_Max"],
                'ProductName':i["ProductName_Max"],
                'OrderingCount':i["OrderingCount_Max"],
                'Shipping_total':i["Shipping_total"],
                'Abs_total':i["Abs_total"],
                'ShippingVolume':i["ShippingVolume_Max"],
                'DetailUnitPrice':i["DetailUnitPrice_Max"],
                'SlipDiv_Max':i["SlipDiv_Max"],
                'OrderNumber':i["OrderNumber_Max"],
                'SlipDiv':i["SlipDiv_Max"],
                'ShippingDate':i["ShippingDate_Max"],
                'Summary':"",
                'Division':'1',
            }
            stock_list.append(stock)

    #請求月支払レコード
    queryset_pay = Payment.objects.filter(PaymentDate__range=(str(search_date[0]),str(search_date[1])),PaymentSupplierCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset_pay = queryset_pay.filter(~Q(PaymentDiv=11))
    queryset_pay =  queryset_pay.values('PaymentDate','PaymentDiv__DepoPayDivname','PaymentSummary','PaymentMoney')
    queryset_pay = list(queryset_pay)
    pay_list = []

    if queryset_pay:
        for i in queryset_pay:
            pay = {
                'InvoiceIssueDate': i["PaymentDate"],
                'SlipNumber':"",
                'ProductName':i["PaymentDiv__DepoPayDivname"],
                'OrderingCount':"",
                'Shipping_total':"",
                'Abs_total':i["PaymentMoney"],
                'ShippingVolume':"",
                'Detailsellprice':"",
                'SlipDiv_Max':"",
                'OrderNumber':"",
                'SlipDiv':i["PaymentMoney"],
                'Summary':i["PaymentSummary"],
                'Division':'2',
            }
            pay_list.append(pay)

    #請求月支払レコード消費税調整
    queryset_adjust = Payment.objects.filter(PaymentDate__range=(str(search_date[0]),str(search_date[1])),PaymentSupplierCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset_adjust = queryset_adjust.filter(PaymentDiv=11)
    queryset_adjust =  queryset_adjust.values('PaymentDate','PaymentDiv__DepoPayDivname','PaymentSummary','PaymentMoney')
    queryset_adjust = list(queryset_adjust)
    adjust_list = []

    if queryset_adjust:
        for i in queryset_adjust:
            adjust = {
                'InvoiceIssueDate': i["PaymentDate"],
                'SlipNumber':"",
                'ProductName':i["PaymentDiv__DepoPayDivname"],
                'OrderingCount':"",
                'Shipping_total':"",
                'Abs_total':"",
                'ShippingVolume':"",
                'Detailsellprice':i["PaymentMoney"],
                'SlipDiv_Max':"",
                'OrderNumber':"",
                'SlipDiv':"",
                'Summary':i["PaymentSummary"],
                'Division':'3',
            }
            adjust_list.append(adjust)



    #繰越レコードと売上レコードと入金レコードを結合
    result = list(chain(stock_list, pay_list, adjust_list))

    return result

if __name__ == '__main__':
    make()   
