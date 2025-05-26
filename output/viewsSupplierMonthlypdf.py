from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B4, landscape  
from myapp.models import CustomerSupplier
from myapp.output import suppliermonthlyfunction, GetPurchasePrevfunction, GetPurchasefunction, viewsGetTaxRateFunction, GetBalancefunction, viewsGetDateFunction
# 検索機能のために追加
from django.db.models import Q
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from decimal import Decimal
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
        filename = "SupplierMonthly_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = viewsGetDateFunction.conversion(TargetMonth)
        result = make(search_date,response, element_From, element_To)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:SupplierMonthlylist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:SupplierMonthlylist")
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
    TaxExemptTotal=0
    total=[]

    if counter==0:
        result=99
        return result
    
    for i in range(counter):
        dt = customer(i, dt_company)
        dt_Prev = PrevBalance(search_date, dt, dt_Taxrate)
        if dt_Prev[0]!=0 or dt_Prev[1]!=0 or dt_Prev[2]!=0 or dt_Prev[3]!=0 or dt_Prev[4]!=0 or dt_Prev[5]!=0:
            width-= 8
            suppliermonthlyfunction.printstring(pdf_canvas, dt, dt_Prev, leng, width, search_date)
            #合計計算
            BillTotal += int(dt_Prev[0])
            SellTotal += int(dt_Prev[3])
            TaxTotal += int(dt_Prev[4])
            SellTaxTotal += int(dt_Prev[3] + dt_Prev[4] + dt_Prev[6])
            TaxExemptTotal += int(dt_Prev[6])
            DepositTotal += int(dt_Prev[1])
            CarryoverTotal += int(dt_Prev[5])

            leng+=1
            if leng!=0 and leng % 25 == 0:
                suppliermonthlyfunction.lineprintstring(pdf_canvas)
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
        suppliermonthlyfunction.blankprintstring(pdf_canvas, width)

    # 合計計算値を配列に
    total.append(str(BillTotal))
    total.append(str(SellTotal))
    total.append(str(TaxTotal))
    total.append(str(SellTaxTotal))
    total.append(str(DepositTotal))
    total.append(str(CarryoverTotal))
    total.append(str(TaxExemptTotal))

    #合計行出力
    width-= 8
    suppliermonthlyfunction.totalprintstring(pdf_canvas, width, total)

    pdf_canvas.showPage()
    pdf_canvas.save() # 保存

    return result

#仕入先月次集計表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("仕入先月次集計表")
    pdf_canvas.setSubject("仕入先月次集計表")
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
                            ).filter(Q(MasterDiv=3) | Q(MasterDiv=4),is_Deleted=0,id__gte=element_From,id__lte=element_To).order_by('CustomerCode'))

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
                                    'LastPayable',
                            ))

    return Customer

def PrevBalance(search_date, Customer, is_taxrate):
    #前月までの支払額計
    DepoPrvSum = GetPurchasePrevfunction.GetPayPrvSum(search_date, Customer)
    #前月までの課税仕入合計額を取得
    SellPrvSum = GetPurchasePrevfunction.GetStockPrvSum(search_date, Customer)
    #前月までの非課税仕入合計額を取得
    PrvTaxExempt = GetPurchasePrevfunction.GetPrvTaxExempt(search_date, Customer)
    #前月までの消費税調整額レコードを取得
    PrvAdjustment = GetPurchasePrevfunction.GetPrevAdjustmentDetail(search_date, Customer)
    #0前月までの支払合計額0判定
    if DepoPrvSum:
        DepoPrvTotal = int(DepoPrvSum[0]['Pay_total'])
    else:
        DepoPrvTotal = 0
    #前月までの非課税仕入額を合計する
    PrvTaxExemptTotal = 0
    if PrvTaxExempt:
        for q in PrvTaxExempt:
            PrvTaxExemptTotal+=int(q['Abs_total'])
    #前月までの消費税調整額を合計する
    PrvAdjust=0
    if PrvAdjustment:
        for i,q in  enumerate(PrvAdjustment):
            PrvAdjust+=int(q['Adjustment_total'])

    #2025-05-21 仕様変更
    array=GetBalancefunction.GetSalesBalance(SellPrvSum,is_taxrate)
  
    #前月繰越額計算
    PrevBill = int(Customer[0]['LastPayable']) - int(DepoPrvTotal) + int(array[0]) + int(array[1]) + int(PrvAdjust) + int(PrvTaxExemptTotal)
    #当月支払合計額
    DepoSum = GetPurchasefunction.GetPaySum(search_date, Customer)
    #0判定
    if DepoSum:
        DepoTotal = int(DepoSum[0]['Pay_total'])
    else:
        DepoTotal = 0
    #次月繰越額計算
    CarryForward = int(PrevBill) - int(DepoTotal)
    #当月支払消費税調整額を取得
    Adjustment = GetPurchasefunction.GetAdjustment(search_date, Customer)
    #当月支払消費税調整額0判定
    if Adjustment:
        AdjustmentTotal = int(Adjustment[0]['Adjustment_total'])
    else:
        AdjustmentTotal = 0

    #当月課税仕入額を取得
    PurchaseTaxRow = GetPurchasefunction.GetPurchaseTaxRow(search_date, Customer)
    #当月課税仕入額を集計
    i=0
    SellTotal=0
    l = len(PurchaseTaxRow)
    queryset = list(PurchaseTaxRow)
    if queryset:
        while i < l:
            row=queryset[i]
            #仕入金額加算
            SellTotal += int(Decimal(row['ShippingVolume']) * Decimal(row['OrderingDetailId__DetailUnitPrice']))
            i+=1
    else:
        tax=0
        invoice=0
        SellTotal = 0

    # 消費税率取得 2025-05-12追加 -----------------------------------------------#
    taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, search_date[0], search_date[1])
    #---------------------------------------------------------------------------#

    #当月仕入消費税額を計算
    #tax = int(SellTotal * 0.1) + int(AdjustmentTotal)
    tax = int(SellTotal * taxrate[0]) + int(AdjustmentTotal)
    tax = int(tax)

    #当月非課税仕入額を取得
    queryset = GetPurchasefunction.GetPurchaseRow(search_date, Customer)
    i=0
    TaxExempt=0
    l = len(queryset)
    queryset = list(queryset)
    if queryset:
        while i < l:
            row=queryset[i]
            #仕入金額加算
            TaxExempt += int(Decimal(row['ShippingVolume']) * Decimal(row['OrderingDetailId__DetailUnitPrice']))
            i+=1
    else:
        TaxExempt = 0

    #当月仕入額を計算
    #SellTotal = int(SellTotal + TaxExempt)
    #当月税込仕入合計額を計算
    invoice = int(CarryForward + SellTotal + tax + TaxExempt)

    return(PrevBill, DepoTotal, CarryForward, SellTotal, tax, invoice, TaxExempt)

if __name__ == '__main__':
    make()   
