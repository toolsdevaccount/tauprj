from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait  
from myapp.models import RequestResult
from myapp.output import RequestCumulativefunction
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta
# 計算用
from django.db.models import Sum,F,DecimalField
from django.db.models.functions import Coalesce
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request, TargetMonthFrom, TargetMonthTo):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "RequestCumulativelist_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        # 文字列を日付に変換する
        search_date = conversion(TargetMonthFrom, TargetMonthTo)
        result = make(search_date,response)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:RequestCumulativelist")
    if result==99:
        message = "発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:RequestCumulativelist")
    return response

def make(search_date, response):
    pdf_canvas = set_info(response) # キャンバス名
    dt = RequestCumulative(search_date)
    counter = len(dt)

    if counter==0:
        result=99
        return result
    
    RequestCumulativefunction.printstring(pdf_canvas, dt, search_date)
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

#得意先月次集計表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("依頼先別売上順一覧")
    pdf_canvas.setSubject("依頼先別売上順一覧")
    return pdf_canvas

def RequestCumulative(search_date):
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            )

    SellSum =  list(queryset.values(
        'OrderingId__RequestCode',
        'OrderingId__RequestCode__CustomerCode',
        'OrderingId__RequestCode__CustomerName',
        ).annotate(
        Sell_total=Sum(
            Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=DecimalField()
            ),
        Supplier_total=Sum(
            Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=DecimalField()            
            )
        ).order_by('Sell_total').reverse())
    return SellSum

if __name__ == '__main__':
    make()   
