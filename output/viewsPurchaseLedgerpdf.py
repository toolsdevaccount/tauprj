from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B4, landscape  
from myapp.models import CustomerSupplier
from myapp.output import purchaseLedgerfunction, GetPurchasefunction, GetPurchasePrevfunction, viewsGetTaxRateFunction, GetBalancefunction
# 検索機能のために追加
from django.db.models import Q
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from itertools import chain
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
    # 消費税率取得
    dt_Taxrate = viewsGetTaxRateFunction.gettaxrate()

    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt = customer(i, dt_company)
        dt_Prev = PrevBalance(search_date, dt, dt_Taxrate)
        dt_Detail = Detail(search_date, dt)

        if dt_Prev[0]!=0 or dt_Prev[6]!=0:
            purchaseLedgerfunction.printstring(pdf_canvas, dt, dt_Prev, dt_Detail, search_date, dt_Taxrate)
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

def PrevBalance(search_date, Customer, is_taxrate): 
    #前月までの支払合計額を取得
    PayPrvSum = GetPurchasePrevfunction.GetPayPrvSum(search_date, Customer)  
    #前月までの課税仕入額を取得
    StockPrvSum = GetPurchasePrevfunction.GetStockPrvSum(search_date, Customer)
    #前月までの非課税仕入額を取得
    PrvTaxExempt = GetPurchasePrevfunction.GetPrvTaxExempt(search_date, Customer)
    #前月までの消費税調整合計額を取得
    Adjustment = GetPurchasePrevfunction.GetPrevAdjustment(search_date, Customer)
    #0判定
    if PayPrvSum:
        PayPrvTotal = int(PayPrvSum[0]['Pay_total'])
    else:
        PayPrvTotal = 0
    #前月までの非課税仕入額を合計する
    PrvTaxExemptTotal = 0
    if PrvTaxExempt:
        for q in PrvTaxExempt:
            PrvTaxExemptTotal+=int(q['Abs_total'])
    #前月までの消費税調整合計額0判定
    if Adjustment:
        AdjustmentTotal = int(Adjustment[0]['Adjustment_total'])
    else:
        AdjustmentTotal = 0

    #前月までの課税仕入額の消費税計算
    #2025-05-23 仕様変更
    array=GetBalancefunction.GetSalesBalance(StockPrvSum, is_taxrate)

    #前回買掛額算出（買掛残高 - 前月までの支払合計額 + 前月までの課税仕入合計額 + 前月までの課税仕入消費税額 + 前月までの非課税仕入額
    PrevBill = int(Customer[0]['LastPayable']) - int(PayPrvTotal) + int(array[0]) + int(array[1]) + int(AdjustmentTotal) + int(PrvTaxExemptTotal)
    #当月支払合計額
    PaySum = GetPurchasefunction.GetPaySum(search_date, Customer)
    #0判定
    if PaySum:
        PayTotal = int(PaySum[0]['Pay_total'])
    else:
        PayTotal = 0
    #買掛金繰越額
    CarryForward = int(PrevBill) - int(PayTotal)
    #当月支払消費税調整額を取得
    Adjustment = GetPurchasefunction.GetAdjustment(search_date, Customer)  
    #当月支払消費税調整額0判定
    if Adjustment:
        AdjustmentTotal = int(Adjustment[0]['Adjustment_total'])
    else:
        AdjustmentTotal = 0
    #当月仕入額を取得
    StockSum = GetPurchasefunction.GetStockSum(search_date, Customer)
    #当月仕入額を合計
    StockTotal = 0
    for d in StockSum:
        StockTotal+=int(d['Abs_total'])

    # 消費税率取得 2025-05-12追加 -----------------------------------------------#
    taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, search_date[0], search_date[1])
    #---------------------------------------------------------------------------#

    #当月仕入消費税額を計算
    tax = int(StockTotal) * taxrate[0] + int(AdjustmentTotal)
    tax = int(tax)
    #当月税込仕入合計額
    invoice = int(CarryForward) + int(StockTotal) + int(tax)
    CarryOver = int(PrevBill) + int(invoice) - int(PayTotal)

    return(PrevBill, PayTotal, CarryForward, StockTotal, tax, invoice, CarryOver)

def Detail(search_date, Customer): 
    #当月課税分仕入レコードを取得
    queryset = list(GetPurchasefunction.GetPurchaseTaxDetail(search_date, Customer))
    stock_list_tax = []
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
            stock_list_tax.append(stock)
    #当月非課税分仕入レコードを取得
    queryset = list(GetPurchasefunction.GetPurchaseDetail(search_date, Customer))
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
                'Division':'1.5',
            }
            stock_list.append(stock)
    #当月支払レコードを取得
    queryset_pay = list(GetPurchasefunction.GetPayDetail(search_date, Customer))
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

    #当月支払消費税調整レコードを取得
    queryset_adjust = list(GetPurchasefunction.GetAdjustmentDetail(search_date, Customer))
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
    #当月課税分仕入、#当月非課税分仕入、当月支払、当月支払消費税調整レコードを結合
    result = list(chain(stock_list_tax, stock_list, pay_list, adjust_list))

    return result

if __name__ == '__main__':
    make()   
