from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B4, landscape  
from myapp.models import Deposit, CustomerSupplier, RequestResult
from myapp.output import salesledgerfunction
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
        filename = "SalesLedger_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
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
        return redirect("myapp:SalesLedgerlist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:SalesLedgerlist")
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
            salesledgerfunction.printstring(pdf_canvas, dt, dt_Prev, dt_Detail, search_date[4], search_date[5])
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
    PrinttDate = PrtDate.strftime('%Y年%m月')

    #繰越年月日
    CurryDate = PrtDate.strftime('%Y/%m/%d')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, PrinttDate, CurryDate)

#売上台帳
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("売上台帳")
    pdf_canvas.setSubject("売上台帳")
    return pdf_canvas

def company(element_From, element_To):
    queryset = CustomerSupplier.objects.filter(is_Deleted=0)
    Company = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'ClosingDate',
                                    'LastReceivable',
                            ).filter(Q(MasterDiv=2) | Q(MasterDiv=4),id__gte=element_From,id__lte=element_To).order_by('CustomerCode'))

    return Company

def customer(i, dt_company):
    queryset = CustomerSupplier.objects.filter(CustomerCode=(str(dt_company[i]['CustomerCode'])),is_Deleted=0)
    Customer = list(queryset.values(
                                    'id',
                                    'CustomerCode',
                                    'CustomerName',
                                    'ClosingDate',
                                    'LastReceivable',
                            ))

    return Customer

def PrevBalance(search_date, Customer): 
    #前月までの入金額計
    queryset = Deposit.objects.filter(DepositDate__lte=(str(search_date[3])),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    DepoPrvSum = list(queryset.values('DepositCustomerCode').annotate(Depo_total=Coalesce(Sum('DepositMoney'),0,output_field=IntegerField())))
    #0判定
    if DepoPrvSum:
        DepoPrvTotal = int(DepoPrvSum[0]['Depo_total'])
    else:
        DepoPrvTotal = 0

    #前月までの売上額計
    SellPrvSum =  RequestResult.objects.annotate(
        monthly=TruncMonth('InvoiceIssueDate')
        ).values(
            'monthly',
            'id',
        ).filter(
            InvoiceIssueDate__lte=(str(search_date[3])),
            OrderingId__CustomeCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            ).annotate(
                    Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=IntegerField()),
                ).order_by(
                    'monthly'
                )

    #残高消費税計算
    tax=0
    SellPrvTotal=0
    Selltax=0
    SellPrvtax=0
    monthly=0
    dcnt = len(SellPrvSum)
    if SellPrvSum:
        for i,q in  enumerate(SellPrvSum):
            if (i!=0 and monthly!=q['monthly']) or i==dcnt-1:
                if i==dcnt-1:
                    tax+= int(q['Abs_total'])
                Selltax=int(tax*0.1)
                SellPrvtax+=Selltax
                tax=0
            SellPrvTotal+=int(q['Abs_total'])
            tax+= int(q['Abs_total'])

            monthly=q['monthly']


    # 前回請求額算出
    PrevBill = int(Customer[0]['LastReceivable']) - int(DepoPrvTotal) + int(SellPrvTotal) + int(SellPrvtax)
    # 当月入金合計額
    queryset = Deposit.objects.filter(DepositDate__range=(str(search_date[0]),str(search_date[1])),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    DepoSum = list(queryset.values('DepositCustomerCode').annotate(Depo_total=Coalesce(Sum('DepositMoney'),0,output_field=IntegerField())))
    #0判定
    if DepoSum:
        DepoTotal = int(DepoSum[0]['Depo_total'])
    else:
        DepoTotal = 0
    # 売掛金繰越額
    CarryForward = int(PrevBill) - int(DepoTotal)   
    # 当月売上合計額
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )

    SellSum =  list(queryset.values(
        'OrderingId__CustomeCode',
        'id',
        ).annotate(
            Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=IntegerField())
            ))
    #0判定
    if SellSum:
        SellTotal = int(SellSum[0]['Abs_total'])
    else:
        SellTotal = 0

    # 当月月売上消費税額
    tax = int(SellTotal) * 0.1
    tax = int(tax)
    # 当月税込売上合計額
    invoice = int(CarryForward) + int(SellTotal) + int(tax)
    CarryOver = int(PrevBill) + int(invoice) - int(DepoTotal)
    # 前回請求額, 入金額合計, 売掛金額, 売上金額, 消費税額, 当月税込売上合計額
    return(PrevBill, DepoTotal, CarryForward, SellTotal, tax, invoice, CarryOver)

def Detail(search_date, Customer): 
    #請求月売上レコード
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                OrderingDetailId__DetailSellPrice__gt=0,
                )
    queryset =  queryset.values(
        'InvoiceNUmber',
        'OrderingId__CustomeCode', 
        'OrderingDetailId__DetailSellPrice',
        'id'
        ).annotate(
            Abs_total=Sum(F('ShippingVolume') * F('OrderingDetailId__DetailSellPrice')),
            Shipping_total=Sum('ShippingVolume'),
            ResultDate_Max=Max('ResultDate'),
            ProductName_Max=Max('OrderingId__ProductName'),
            OrderingCount_Max=Max('OrderingId__OrderingCount'),
            SlipDiv_Max=Max('OrderingId__SlipDiv'),
            OrderNumber_Max=Max('OrderingId__OrderNumber'),
            InvoiceNUmber_Max=Max('InvoiceNUmber'),
            ShippingVolume_Max=Max('ShippingVolume'),
            Detailsellprice_Max=Max('OrderingDetailId__DetailSellPrice'),
            InvoiceIssueDate_Max=Max('InvoiceIssueDate'),
            ).order_by(
                'InvoiceIssueDate',
                'InvoiceNUmber'
                )
    queryset = list(queryset)
    sales_list = []

    if queryset:
        for i in queryset:
            sales = {
                'InvoiceIssueDate': i["InvoiceIssueDate_Max"],
                'InvoiceNUmber':i["InvoiceNUmber_Max"],
                'ProductName':i["ProductName_Max"],
                'OrderingCount':i["OrderingCount_Max"],
                'Shipping_total':i["Shipping_total"],
                'Abs_total':i["Abs_total"],
                'ShippingVolume':i["ShippingVolume_Max"],
                'Detailsellprice':i["Detailsellprice_Max"],
                'SlipDiv_Max':i["SlipDiv_Max"],
                'OrderNumber':i["OrderNumber_Max"],
                'SlipDiv':i["SlipDiv_Max"],
                'Summary':"",
                'Division':'1',
            }
            sales_list.append(sales)

    #請求月入金レコード
    queryset_depo = Deposit.objects.filter(DepositDate__range=(str(search_date[0]),str(search_date[1])),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    queryset_depo =  queryset_depo.values('DepositDate','DepositDiv__DepoPayDivname','DepositSummary','DepositMoney')
    queryset_depo = list(queryset_depo)
    depo_list = []

    if queryset_depo:
        for i in queryset_depo:
            depo = {
                'InvoiceIssueDate': i["DepositDate"],
                'InvoiceNUmber':"",
                'ProductName':i["DepositDiv__DepoPayDivname"],
                'OrderingCount':"",
                'Shipping_total':"",
                'Abs_total':i["DepositMoney"],
                'ShippingVolume':"",
                'Detailsellprice':"",
                'SlipDiv_Max':"",
                'OrderNumber':"",
                'SlipDiv':i["DepositMoney"],
                'Summary':i["DepositSummary"],
                'Division':'2',
            }
            depo_list.append(depo)

    #繰越レコードと売上レコードと入金レコードを結合
    result = list(chain(sales_list, depo_list))

    return result

if __name__ == '__main__':
    make()   
