from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B4, landscape  
from myapp.models import Deposit, CustomerSupplier, RequestResult
from myapp.output import customermonthlyfunction, viewsGetTaxRateFunction
# 検索機能のために追加
from django.db.models import Q
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.db.models.functions import TruncMonth
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)
#pandas
import pandas as pd

def pdf(request, TargetMonth, element_From, element_To):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "CustomerMonthly_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = conversion(TargetMonth)
        result = make(search_date, response, element_From, element_To)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:CustomerMonthlylist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:CustomerMonthlylist")
    return response

def make(search_date, response, element_From, element_To):
    pdf_canvas = set_info(response) # キャンバス名
    dt_company = company(element_From, element_To)
    counter = len(dt_company)
    # 消費税率取得
    dt_Taxrate = viewsGetTaxRateFunction.gettaxrate()

    # 初期値
    leng=0
    width=220
    # 計算用
    BillTotal=0
    SellTotal=0
    TaxTotal=0
    SellTaxTotal=0
    DepositTotal=0
    CarryoverTotal=0
    total=[]

    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt = customer(i, dt_company)
        dt_Prev = PrevBalance(search_date, dt, dt_Taxrate)
        if dt_Prev[0]!=0 or dt_Prev[1]!=0 or dt_Prev[2]!=0 or dt_Prev[3]!=0 or dt_Prev[4]!=0 or dt_Prev[5]!=0:
            width-= 8
            customermonthlyfunction.printstring(pdf_canvas, dt, dt_Prev, leng, width, search_date)
            #合計計算
            BillTotal += Decimal(dt_Prev[0])
            SellTotal += Decimal(dt_Prev[3])
            TaxTotal += Decimal(dt_Prev[4])
            SellTaxTotal += Decimal(dt_Prev[3])+Decimal(dt_Prev[4])
            DepositTotal += Decimal(dt_Prev[1])
            CarryoverTotal += Decimal(dt_Prev[5])

            leng+=1
            if leng!=0 and leng % 25 == 0:
                customermonthlyfunction.lineprintstring(pdf_canvas)
                pdf_canvas.showPage()
                width=220
 
        result=0

    #2025-05-21 0件対策
    if leng==0:
        result=99
        return result

    # 空白行を出力
    number = (24-leng)
    for i in range(number):
        width-= 8
        customermonthlyfunction.blankprintstring(pdf_canvas, width)

    # 合計計算値を配列に
    total.append(str(BillTotal))
    total.append(str(SellTotal))
    total.append(str(TaxTotal))
    total.append(str(SellTaxTotal))
    total.append(str(DepositTotal))
    total.append(str(CarryoverTotal))

    #合計行出力
    width-= 8
    customermonthlyfunction.totalprintstring(pdf_canvas, width, total)

    pdf_canvas.showPage()
    pdf_canvas.save() # 保存

    return result

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

#得意先月次集計表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("得意先月次集計表")
    pdf_canvas.setSubject("得意先月次集計表")
    return pdf_canvas

def company(element_From, element_To):
    queryset = CustomerSupplier.objects.filter(is_Deleted=0)
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
                                    'LastReceivable',
                            ).filter(Q(MasterDiv=2) | Q(MasterDiv=4),is_Deleted=0,id__gte=element_From,id__lte=element_To).order_by('CustomerCode'))

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
                                    'LastReceivable',
                            ))

    return Customer

def PrevBalance(search_date, Customer, is_taxrate): 
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
                    'monthly',
                )

    tax=0
    SellPrvTotal=0
    SellPrvtax=0

    #2025-05-21 仕様変更
    if SellPrvSum:
        #月ごとに売上金額集計-----------------------------------------------#
        tbl_array = []
        for tbl in SellPrvSum:
            tbldate = tbl['monthly']
            tbldate = datetime.date(tbldate.year , tbldate.month, 1)              
            tbl_array.append([tbldate,tbl['Abs_total']])

        dtfrmae = pd.DataFrame(tbl_array)
        prvsalessum = dtfrmae[[0,1]].groupby([0], as_index =False).sum()
        _tuple =  [tuple(x) for x in prvsalessum.values]

        #残高&消費税計算----------------------------------------------------#
        for q in _tuple:
            # 消費税率取得 2025-05-12追加-----------------------------------------------------------------------------------#
            taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, q[0].strftime('%Y-%m-%d'), q[0].strftime('%Y-%m-%d'))
            #-------------------------------------------------------------------------------------------------------------#
            SellPrvTotal+=int(q[1])
            tax = int(q[1])
            SellPrvtax+= int(tax * taxrate)

    #前回請求額算出
    PrevBill = int(Customer[0]['LastReceivable']) - int(DepoPrvTotal) + int(SellPrvTotal) + int(SellPrvtax)
    #当月入金合計額
    queryset = Deposit.objects.filter(DepositDate__range=(str(search_date[0]),str(search_date[1])),DepositCustomerCode=(str(Customer[0]['id'])),is_Deleted=0)
    DepoSum = list(queryset.values('DepositCustomerCode').annotate(Depo_total=Coalesce(Sum('DepositMoney'),0,output_field=IntegerField())))

    #0判定
    if DepoSum:
        DepoMoneyTotal = int(DepoSum[0]['Depo_total'])
    else:
        DepoMoneyTotal = 0
    if DepoMoneyTotal!=0:
        DepoTotal = int(DepoSum[0]['Depo_total'])
    else:
        DepoTotal = 0
    #売掛金繰越額
    CarryForward = int(PrevBill - DepoTotal)   
    #当月売上合計額
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__CustomeCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0
                )
    SellSum =  list(queryset.values(
        'OrderingId__CustomeCode',
        'InvoiceNUmber', 
        'id',
        ).annotate(
        Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=IntegerField())
        ))

    SellTotal = 0
    for d in SellSum:
        SellTotal+=int(d['Abs_total'])

    # 消費税率取得 2025-05-12追加 -----------------------------------------------#
    taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, search_date[0], search_date[1])
    #---------------------------------------------------------------------------#

    #当月売上消費税額
    #tax = int(SellTotal) * 0.1
    tax = int(SellTotal) * taxrate
    tax = int(tax)
    #当月税込売上合計額
    invoice = int(CarryForward + SellTotal + tax)
    return(PrevBill, DepoTotal, CarryForward, SellTotal, tax, invoice)

if __name__ == '__main__':
    make()   
