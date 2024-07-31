from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
import math
from decimal import Decimal
import datetime

def printstring(pdf_canvas, dt_Detail, PrtDate):
    # フォント登録
    Yumin = "yumin.ttf"
    pdfmetrics.registerFont(TTFont('游明朝 標準', Yumin))
    #style
    styleLeft = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_LEFT)
    styleRight = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_RIGHT)
    styleCenter = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)

    #レコード数
    rec = len(dt_Detail)
    if rec==0:
        rec=1
    #行数
    param=25
    #ページ数
    req = math.ceil(rec/param)

    for t in range(req):
        # 表題
        font_size = 16
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(340, 560, '未　払　一　覧　表')

        # 対象年月
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 540, '対象年月：')
        pdf_canvas.drawString(100, 540, PrtDate + '分')

        # 仕入先
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 520, '仕入先：')
        pdf_canvas.drawString(100, 520, dt_Detail[0]['OrderingId__SupplierCode_id__CustomerCode'] + ' ' + dt_Detail[0]['OrderingId__SupplierCode_id__CustomerName'])

        #出力日時
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        time = datetime.datetime.now()
        str_time = time.strftime('%Y年%m月%d日 %H:%M:%S')
        pdf_canvas.drawString(690, 520, str(str_time))

        # テーブルの項目名
        itemNo0 = Paragraph('請求書発行日',styleCenter)
        itemNo1 = Paragraph('依頼NO',styleCenter)
        itemNo2 = Paragraph('伝票NO',styleLeft)
        itemNo3 = Paragraph('商品名',styleLeft)
        itemNo4 = Paragraph('番手',styleLeft)
        itemNo5 = Paragraph('数量',styleRight)
        itemNo6 = Paragraph('単価',styleRight)
        itemNo7 = Paragraph('仕入金額',styleRight)
        itemNo8 = Paragraph('摘要',styleLeft)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8],
        ]
        table = Table(data, colWidths=(30*mm, 30*mm, 20*mm, 40*mm, 20*mm, 20*mm, 20*mm, 30*mm, 65*mm), rowHeights=6.5*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEABOVE', (0, 0), (8, 0), 1.00, colors.black),
                ('LINEBELOW', (0, 0), (8, 0), 1.00, colors.black),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 170.0*mm)

        if t==0:
            k=0
        else:
            k = t*param
        rowlg = (t+1)*param

        data =[]
        item=0
        item1=0
        item2=0
        item3=0
        item4=0
        while k < rowlg:
            if k<rec and len(dt_Detail)>0:
                row = dt_Detail[k]
                #出荷日
                startdate = row['InvoiceIssueDate'].strftime('%Y年%m月%d日')
                ShippingDate = Paragraph(startdate,styleCenter)
                #依頼No
                OrderNumber = Paragraph(row['OrderingId__SlipDiv'] + '-' + row['OrderingId__OrderNumber'] ,styleCenter)
                #伝票No
                SlipNumber = Paragraph(row['SlipNumber'],styleLeft)
                #商品名
                ProductName = Paragraph(row['OrderingId__ProductName'],styleLeft)
                #番手
                OrderingCount = Paragraph(row['OrderingId__OrderingCount'],styleLeft)
                #数量
                Volume = Paragraph('{:,.2f}'.format(row['OrderingDetailId__DetailVolume']),styleRight)
                #単価
                UnitPrice = Paragraph(f"{int(row['OrderingDetailId__DetailUnitPrice']):,}",styleRight)
                #仕入金額
                SuppTotal = Paragraph(f"{int(row['Supplier_total']):,}",styleRight)
                item1 += Decimal(row['Supplier_total'])
                Summary = Paragraph(row['OrderingDetailId__DetailSummary'],styleLeft)

                data += [
                        [ShippingDate, OrderNumber, SlipNumber, ProductName, OrderingCount, Volume, UnitPrice, SuppTotal, Summary],
                ]
            elif k==(param-1) and t==(req-1):
                #最終行
                #仕入金額合計
                SellPriceTotal = Paragraph(f"{int(item1):,}",styleRight)
                text= Paragraph('合' + '&nbsp&nbsp&nbsp&nbsp' + '計',styleCenter)

                data += [
                        [text, '', '', '', '', '', '', SellPriceTotal, '', ],
                ]
            else:
                data += [
                        ['', '', '', '', '', '', '', '', '',],
                ]

            table = Table(data, colWidths=(30*mm, 30*mm, 20*mm, 40*mm, 20*mm, 20*mm, 20*mm, 30*mm, 65*mm), rowHeights=6.5*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                    ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ]))
            # 変数加算
            k+=1

        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 5*mm)

        pdf_canvas.showPage()
