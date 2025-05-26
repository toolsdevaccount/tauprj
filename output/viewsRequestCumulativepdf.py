from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait  
from myapp.models import RequestResult
from myapp.output import RequestCumulativefunction, viewsGetDateFunction
# 日時
from django.utils import timezone
import datetime
# 計算用
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce
# メッセージ
from django.contrib import messages
#pandas
import pandas as pd
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
        search_date = viewsGetDateFunction.convFromTo(TargetMonthFrom, TargetMonthTo)
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

#得意先月次集計表
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("依頼先別売上順一覧")
    pdf_canvas.setSubject("依頼先別売上順一覧")
    return pdf_canvas

def RequestCumulative(search_date):
    queryset =  RequestResult.objects.filter(
        InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
        InvoiceNUmber__gt=0,
        InvoiceIssueDiv=1,
        is_Deleted=0,
        )

    SellSum =  list(queryset.values(
        'OrderingId__RequestCode',
        'OrderingId__RequestCode__CustomerCode',
        'OrderingId__RequestCode__CustomerName',
        'id',
        ).annotate(
        Sell_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailSellPrice'),0),output_field=IntegerField()),
        Supplier_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField())
        ).order_by('OrderingId__RequestCode'))

    #--------------------------------------------------------------------#
    df = pd.DataFrame(SellSum, columns=['OrderingId__RequestCode','OrderingId__RequestCode__CustomerCode','OrderingId__RequestCode__CustomerName','id','Sell_total','Supplier_total'])
    sales_sum = df[['OrderingId__RequestCode','OrderingId__RequestCode__CustomerCode','OrderingId__RequestCode__CustomerName','Sell_total','Supplier_total']].groupby(['OrderingId__RequestCode','OrderingId__RequestCode__CustomerCode','OrderingId__RequestCode__CustomerName'], as_index=False).sum()
    sales_sum = sales_sum.sort_values('Sell_total', ascending=False)
    list_from_df = sales_sum.values.tolist()
    #--------------------------------------------------------------------#

    return list_from_df

if __name__ == '__main__':
    make()   
