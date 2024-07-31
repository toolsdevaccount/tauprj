from django.http import HttpResponse
from django.shortcuts import redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import B5, portrait, landscape
from myapp.models import CustomerSupplier, OrderingTable
from myapp.output import orderfunction,orderfunctionstain
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request,pk):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "PurchaseOrder_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)

        make(pk,response)
        UpdateQuery(pk)

    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.add_message(request, messages.ERROR, message)
        return redirect("myapp:orderinglist")
    return response

def make(pk,response):
    dt_own = Own_Company()
    dt = connect(pk)
    if dt[0]['OutputDiv']==1:
        pdf_canvas = set_info(response) # キャンバス名
        print_string(pdf_canvas,dt,dt_own)
    if dt[0]['OutputDiv']==2 or dt[0]['OutputDiv']==3:
        pdf_canvas = set_info_stain(response) # キャンバス名
        print_string_StainRequest(pdf_canvas,dt,dt_own)
    pdf_canvas.save() # 保存

#発注書
def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=landscape(B5))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("発注書")
    pdf_canvas.setSubject("発注書")

    return pdf_canvas

#染色依頼書
def set_info_stain(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(B5))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("染色依頼書")
    pdf_canvas.setSubject("染色依頼書")

    return pdf_canvas

def UpdateQuery(pk):
    #更新処理
    result = OrderingTable.objects.filter(id=str(pk)).update(is_Ordered=True)

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
                                ))

    return Own_Company

def connect(pk):
    queryset = OrderingTable.objects.filter(id=(str(pk)),OrderingTableId__PrintDiv=(str(1)),OrderingTableId__is_Deleted=(str(0)))
    result = list(queryset.values(
                                    'OutputDiv',
                                    'SlipDiv',
                                    'OrderNumber',
                                    'OrderingDate',
                                    'ProductName',
                                    'OrderingCount',
                                    'StainPartNumber',
                                    'SupplierPerson',
                                    'TitleDiv',
                                    'ManagerCode__first_name',
                                    'ManagerCode__last_name',
                                    'StainMixRatio',
                                    'StainShippingDate',
                                    'DestinationCode__CustomerName',
                                    'ShippingCode__CustomerName',
                                    'ShippingCode__PostCode',
                                    'ShippingCode__PrefecturesCode__prefecturename',
                                    'ShippingCode__Municipalities',
                                    'ShippingCode__Address',
                                    'ShippingCode__BuildingName',
                                    'ShippingCode__PhoneNumber',
                                    'OrderingTableId__DetailItemNumber',
                                    'OrderingTableId__DetailColorNumber',
                                    'OrderingTableId__DetailColor',
                                    'OrderingTableId__DetailVolume',
                                    'OrderingTableId__DetailUnitDiv',
                                    'OrderingTableId__DetailUnitPrice',
                                    'OrderingTableId__SpecifyDeliveryDate',
                                    'OrderingTableId__StainAnswerDeadline',
                                    'OrderingTableId__DetailSummary',
                                    'StainShippingCode__CustomerName',
                                    'ApparelCode__CustomerName',
                                ))
    return result
#発注書発行
def print_string(pdf_canvas,dt,dt_own):
    orderfunction.printstring(pdf_canvas,dt,dt_own)

if __name__ == '__main__':
    make()

#染色依頼書発行
def print_string_StainRequest(pdf_canvas,dt,dt_own):
    orderfunctionstain.printstringStainRequest(pdf_canvas,dt,dt_own)

if __name__ == '__main__':
    make()
