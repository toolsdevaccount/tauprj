from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait  
from myapp.models import RequestResult
from django.contrib.auth import get_user_model
from myapp.output import salespersonfunction
# 日時
from django.utils import timezone
import datetime
# 計算用
from django.db.models import Sum,F,DecimalField,Max
from django.db.models.functions import Coalesce
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request, TargetMonthFrom, TargetMonthTo, TargetUserFrom, TargetUserTo):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "SalesPersonlist_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = conversion(TargetMonthFrom, TargetMonthTo)
        result = make(search_date, TargetUserFrom, TargetUserTo, response)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:SalesPersonlist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:SalesPersonlist")
    return response

def make(search_date, TargetUserFrom, TargetUserTo, response):
    pdf_canvas = set_info(response) # キャンバス名
    if str(TargetUserFrom)=='0' and str(TargetUserTo)=='0':
        dt_manager=ManagerAll()
    else:
        dt_manager=Manager(TargetUserFrom, TargetUserTo)

    counter = len(dt_manager)

    if counter==0:
        result=99
        return result
    for i in range(counter):   
        dt = SalesPerson(search_date,dt_manager[i]['id'])
        managername = str(dt_manager[i]['first_name'] + dt_manager[i]['last_name'])
        salespersonfunction.printstring(pdf_canvas, dt, search_date, managername)
    pdf_canvas.save() # 保存
    result=0

    return result

def conversion(TargetMonthFrom, TargetMonthTo):
    # 日付型に変換する
    startdate = datetime.datetime.strptime(str(TargetMonthFrom), '%Y%m%d')
    lastdate =  datetime.datetime.strptime(str(TargetMonthTo), '%Y%m%d')

    # 日付型に変換する(YYYY年mm月dd日用)
    strstart = datetime.datetime.strptime(str(TargetMonthFrom), '%Y%m%d')
    strlast = datetime.datetime.strptime(str(TargetMonthTo), '%Y%m%d')

    # 前月初日、末日を算出する

    # From
    startdate = startdate.strftime('%Y-%m-%d')
    # To
    lastdate = lastdate.strftime('%Y-%m-%d')
    # From(YYYY年mm月dd日用)
    strstart = strstart.strftime('%Y年%m月%d日')
    # To(YYYY年mm月dd日用)
    strlast = strlast.strftime('%Y年%m月%d日')

    return(startdate, lastdate, strstart, strlast)

#担当者別売上一覧表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("担当者別売上一覧")
    pdf_canvas.setSubject("担当者別売上一覧")
    return pdf_canvas

def Manager(TargetUserFrom,TargetMonthTo):
    queryset = list(get_user_model().objects.values(
        'id',
        'first_name',
        'last_name').filter(
            id__range=(str(TargetUserFrom),str(TargetMonthTo))
            ).order_by('id'))
    
    return queryset

def ManagerAll():
    queryset = list(get_user_model().objects.values('id','first_name','last_name').order_by('id'))
    
    return queryset

def SalesPerson(search_date, manager):
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            #OrderingId__ManagerCode__id=str(manager),
            OrderingId__RequestCode__ManagerCode__id=str(manager),
            is_Deleted=0,
            )

    SellSum =  list(queryset.values(
        'OrderingId__RequestCode__ManagerCode__id',
        'OrderingId__RequestCode_id'
        ).annotate(
        ManagerCode=Max('OrderingId__RequestCode__ManagerCode__id'),
        RequestCode=Max('OrderingId__RequestCode_id'),
        CustomerCode=Max('OrderingId__RequestCode__CustomerCode'),
        CustomerName=Max('OrderingId__RequestCode__CustomerName'),
        Sell_total=Sum(
            Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=DecimalField()
            ),
        Supplier_total=Sum(
            Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=DecimalField()            
            )
        ).order_by('OrderingId__RequestCode__ManagerCode__id'))

    return SellSum

if __name__ == '__main__':
    make()   
