from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B5, landscape
from myapp.models import RequestResult,CustomerSupplier 
from django.db.models.functions import Concat,Abs
from django.db.models import F,Value
from myapp.output import indiinvoicefunction
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "IndividualInvoice_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        #Getパラメータ
        pkfrom = request.GET.get("inv_from")
        pkto = request.GET.get("inv_to")
        isdate = request.GET.get("inv_date")

        pkfromdef = pkfrom  # 個別請求書番号初期値をコピー
        result = make(pkfrom,pkto,isdate,response)
        cnt = 0
        cnt = int(pkto) - int(pkfromdef) +1
        for i in range(cnt):
            if i>0:
                pkfromdef= int(pkfromdef)+1
            UpdateQuery(pkfromdef,isdate)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:individualinvoicelist")
    if result==99:
        message = "請求書発行データがありません"
        messages.add_message(request, messages.WARNING, message)
        return redirect("myapp:individualinvoicelist")

    return response

def make(pkfrom,pkto,isdate,response):
    pdf_canvas = set_info(response) # キャンバス名
    cnt = int(pkto) - int(pkfrom)+1
    prcnt=0

    dt_own = Own_Company()
    for i in range(cnt):
        if i>0:
            pkfrom=int(pkfrom)+1
        dt = connect(pkfrom,isdate)
        if len(dt)==0:
            # ループの先頭に戻る
            continue
        print_string(pdf_canvas,dt,dt_own)
        prcnt = 1

    if prcnt!=0:
        pdf_canvas.save() # 保存
    else:
        return 99

#個別請求書
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B5))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("納品書")
    pdf_canvas.setSubject("納品書")
    return pdf_canvas

def UpdateQuery(pkfromdef,isdate):
    #日付変換
    tdate = datetime.datetime.strptime(str(isdate), '%Y%m%d')
    date_up = tdate.strftime('%Y-%m-%d') 
    #更新処理
    result = RequestResult.objects.filter(InvoiceNUmber=str(pkfromdef)).update(InvoiceIssueDate=date_up, InvoiceIssueDiv=True)

    return result

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
                                ).annotate(OwnAddress=Concat('PrefecturesCode__prefecturename',
                                           'Municipalities','Address','BuildingName')
                        ))

    return Own_Company

def connect(pkfrom,isdate):
    queryset =  RequestResult.objects.filter(InvoiceNUmber=(str(pkfrom)),OrderingDetailId__DetailSellPrice__gt=0,is_Deleted=0)
    result = list(queryset.values(
                            'InvoiceNUmber',
                            'OrderingId__SlipDiv',
                            'OrderingId__OrderNumber',
                            'OrderingId__CustomeCode_id__PostCode',
                            'OrderingId__CustomeCode_id__CustomerName',
                            'OrderingId__CustomeCode_id__PrefecturesCode__prefecturename',
                            'OrderingId__CustomeCode_id__Municipalities',
                            'OrderingId__CustomeCode_id__Address',
                            'OrderingId__CustomeCode_id__BuildingName',
                            'OrderingId__ShippingCode_id__CustomerName',
                            'ShippingDate',
                            'OrderingId__ProductName',
                            'OrderingId__OrderingCount',
                            'OrderingDetailId__DetailColorNumber',
                            'OrderingDetailId__DetailColor',
                            'ShippingVolume',
                            'OrderingDetailId__DetailSellPrice',
                            'OrderingDetailId__DetailUnitDiv',
                            'ResultSummary',
                            'OrderingId__CustomeCode_id__CustomerCode',                           
                        ).annotate(
                            Address = Concat('OrderingId__CustomeCode_id__PrefecturesCode__prefecturename',
                                             'OrderingId__CustomeCode_id__Municipalities',
                                             'OrderingId__CustomeCode_id__Address'),
                            OrderNumber=Concat('OrderingId__SlipDiv',Value('-'),'OrderingId__OrderNumber'),
                            SellPrice=F("ShippingVolume") * F("OrderingDetailId__DetailSellPrice"),
                            IssueDate=Value(isdate),
                        ).order_by('InvoiceNUmber','ShippingDate','OrderingDetailId__DetailItemNumber'))
    return result
#個別請求書発行
def print_string(pdf_canvas,dt,dt_own):
    indiinvoicefunction.printstring(pdf_canvas,dt,dt_own)

if __name__ == '__main__':
    make()   
