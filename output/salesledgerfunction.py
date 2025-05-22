from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
import math
from decimal import Decimal
from myapp.output import viewsGetTaxRateFunction

def printstring(pdf_canvas, dt, dt_Prev, dt_Detail, search_date, is_taxrate):
    # フォント登録
    Yumin = "yumin.ttf"
    pdfmetrics.registerFont(TTFont('游明朝 標準', Yumin))
    #レコード数
    rec = len(dt_Detail)
    if rec==0:
        rec=1
    #行数
    param=20
    #ページ数
    req = math.ceil(rec/param)
    #余りがでるか確認
    remainder = rec%param
    if remainder==0:
        req+=1

    for t in range(req):
        # 表題
        font_size = 16
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(420, 670, '売　上　台　帳')

        # 得意先名
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 640, dt[0]['CustomerCode'] + ' ' + dt[0]['CustomerName'])
        # 線の太さ
        pdf_canvas.setLineWidth(0.25)
        # 下線
        pdf_canvas.line(30, 632, 240, 632) 
        # 敬称（様固定）
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(225, 640, '様')

        # テーブルの項目名
        style = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)
        itemNo0 = Paragraph('年月日',style)
        itemNo1 = Paragraph('個請NO',style)
        itemNo2 = Paragraph('依頼NO',style)
        itemNo3 = Paragraph('商品名',style)
        itemNo4 = Paragraph('番手',style)
        itemNo5 = Paragraph('数量',style)
        itemNo6 = Paragraph('単価',style)
        itemNo7 = Paragraph('売上金額',style)
        itemNo8 = Paragraph('個済',style)
        itemNo9 = Paragraph('一済',style)
        itemNo10 = Paragraph('消費税額',style)
        itemNo11 = Paragraph('前月繰越額',style)
        itemNo12 = Paragraph('入金額',style)
        itemNo13 = Paragraph('摘要',style)
        itemNo14 = Paragraph('差引金額',style)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8, itemNo9, itemNo10, itemNo11, itemNo12, itemNo13, itemNo14],
        ]
        table = Table(data, colWidths=(22*mm, 18*mm, 20*mm, 38*mm, 18*mm, 18*mm, 20*mm, 25*mm, 12*mm, 12*mm, 25*mm, 25*mm, 25*mm, 24*mm, 25*mm), rowHeights=8.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.50,  colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 210.0*mm)

        if t==0:
            k=0
        else:
            k = t*param
        rowlg = (t+1)*param

        styleLeft = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_RIGHT)

        #繰越
        if t==0:
            ProductName = '繰越'
            PrevBill = Paragraph(f"{int(dt_Prev[0]):,}",styleRight)
       
            data = [
                    [search_date[5], '', '', ProductName, '', '', '', '',
                        '', '', '', PrevBill, '', '', PrevBill],
            ]
        else:
            data = [
                    ['', '', '', '', '', '', '', '',
                        '', '', '', '', '', '', ''],
            ]

        table = Table(data, colWidths=(22*mm, 18*mm, 20*mm, 38*mm, 18*mm, 18*mm, 20*mm, 25*mm, 12*mm, 12*mm, 25*mm, 25*mm, 25*mm, 24*mm, 25*mm), rowHeights=8.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('LINEBEFORE', (0, 0), (0, -1), 0.50, colors.black),
                ('LINEBEFORE', (1, 0), (1, -1), 0.50, colors.black),
                ('LINEBEFORE', (2, 0), (2, -1), 0.50, colors.black),
                ('LINEBEFORE', (3, 0), (3, -1), 0.50, colors.black),
                ('LINEBEFORE', (4, 0), (4, -1), 0.50, colors.black),
                ('LINEBEFORE', (5, 0), (5, -1), 0.50, colors.black),
                ('LINEBEFORE', (6, 0), (6, -1), 0.50, colors.black),
                ('LINEBEFORE', (7, 0), (7, -1), 0.50, colors.black),
                ('LINEBEFORE', (8, 0), (8, -1), 0.50, colors.black),
                ('LINEBEFORE', (9, 0), (9, -1), 0.50, colors.black),
                ('LINEBEFORE', (10, 0), (10, -1), 0.50, colors.black),
                ('LINEBEFORE', (11, 0), (11, -1), 0.50, colors.black),
                ('LINEBEFORE', (12, 0), (12, -1), 0.50, colors.black),
                ('LINEBEFORE', (13, 0), (13, -1), 0.50, colors.black),
                ('LINEBEFORE', (14, 0), (14, -1), 0.50, colors.black),
                ('LINEAFTER', (14, 0), (14, -1), 0.50, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 202*mm)

        data =[]
        if t==0:
            item = Decimal(dt_Prev[0])       
            item1=0
            item2=0
            item3=0
            item4=0

        while k < rowlg:
            if k<rec and len(dt_Detail)>0:
                row = dt_Detail[k]
                #年月日
                startdate = row['InvoiceIssueDate'].strftime('%Y/%m/%d')
                InvoiceIssueDate = Paragraph(startdate,styleLeft)
                #個別請求書NO、番手
                InvoiceNo = Paragraph(row['InvoiceNUmber'],styleRight)
                OrderingCount = Paragraph(row['OrderingCount'],styleLeft)
                #商品名
                ProductName = Paragraph(row['ProductName'],styleLeft)
                #オーダーNO(依頼NO)
                if row['Division']=='1':
                    OrderNumber = Paragraph(row['SlipDiv_Max']+'-'+row['OrderNumber'],styleLeft)
                else:
                    OrderNumber = Paragraph('',styleLeft)
                #数量
                if row['Division']=='1':
                    ShippingVol = Paragraph('{:,.2f}'.format(row['Shipping_total']),styleRight)
                else:
                    ShippingVol = Paragraph('',styleRight)
                #単価
                if row['Division']=='1':
                    if int(row['Detailsellprice'])!=0:
                        SellPrice = Paragraph(f"{int(row['Detailsellprice']):,}",styleRight)
                    else:
                        SellPrice = Paragraph('',styleRight)
                else:
                    SellPrice = Paragraph('',styleRight)
                #売上金額
                if row['Division']=='1':
                    if int(row['Abs_total'])!=0:
                        SellTotal = Paragraph(f"{int(row['Abs_total']):,}",styleRight)
                    else:
                        SellTotal = Paragraph('',styleRight)
                    item1 += int(row['Abs_total'])
                else:
                    SellTotal = Paragraph('',styleRight)
                #入金額,摘要
                if row['Division']=='1':
                    Summary = Paragraph('',styleLeft)
                    Depo = Paragraph('',styleRight)
                elif row['Division']=='2':
                    Summary = Paragraph(row['Summary'],styleLeft)
                    Depo = Paragraph(f"{int(row['SlipDiv']):,}",styleRight)
                    item2 += Decimal(row['SlipDiv'])
                #前回繰越額
                if row['Division']=='1':
                    item += int(row['Abs_total'])
                elif row['Division']=='2':
                    item -= Decimal(row['SlipDiv'])
                Deduction = Paragraph(f"{int(item):,}",styleRight)
                data += [
                        [InvoiceIssueDate, InvoiceNo, OrderNumber, ProductName, OrderingCount, ShippingVol, SellPrice, SellTotal,
                         '', '', '', '', Depo, Summary, Deduction],
                ]
            #elif k==(param-1) and t==(req-1):
            elif k==(rowlg-1) and t==(req-1):
                #最終行
                #売上金額合計
                if item1==0:
                    SellPriceTotal = Paragraph('',styleRight)
                else:
                    SellPriceTotal = Paragraph(f"{int(item1):,}",styleRight)
                #前回繰越額
                PrvBillTotal = Paragraph(f"{int(dt_Prev[0]):,}",styleRight)
                #入金額合計
                if item2==0:
                    DepoTotal = Paragraph('',styleRight)
                else:
                    DepoTotal = Paragraph(f"{int(item2):,}",styleRight)

                #合計消費税額
                # 消費税率取得 2025-05-12追加 -----------------------------------------------#
                taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, search_date[0], search_date[1])
                #---------------------------------------------------------------------------#

                item3 = int(item1 * taxrate)
                if item3==0:
                    TaxTotal = Paragraph('',styleRight)
                else:
                    TaxTotal = Paragraph(f"{int(item3):,}",styleRight)

                #次回繰越額
                item4 = int(item + item3)
                Total = Paragraph(f"{int(item4):,}",styleRight)

                data += [
                        ['', '', '', '', '', '', '', SellPriceTotal, '', '', TaxTotal, PrvBillTotal, DepoTotal, '', Total],
                ]
            else:
                data += [
                        ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ]

            table = Table(data, colWidths=(22*mm, 18*mm, 20*mm, 38*mm, 18*mm, 18*mm, 20*mm, 25*mm, 12*mm, 12*mm, 25*mm, 25*mm, 25*mm, 24*mm, 25*mm), rowHeights=8.0*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                    ('LINEBEFORE', (0, 0), (0, -1), 0.50, colors.black),
                    ('LINEBEFORE', (1, 0), (1, -1), 0.50, colors.black),
                    ('LINEBEFORE', (2, 0), (2, -1), 0.50, colors.black),
                    ('LINEBEFORE', (3, 0), (3, -1), 0.50, colors.black),
                    ('LINEBEFORE', (4, 0), (4, -1), 0.50, colors.black),
                    ('LINEBEFORE', (5, 0), (5, -1), 0.50, colors.black),
                    ('LINEBEFORE', (6, 0), (6, -1), 0.50, colors.black),
                    ('LINEBEFORE', (7, 0), (7, -1), 0.50, colors.black),
                    ('LINEBEFORE', (8, 0), (8, -1), 0.50, colors.black),
                    ('LINEBEFORE', (9, 0), (9, -1), 0.50, colors.black),
                    ('LINEBEFORE', (10, 0), (10, -1), 0.50, colors.black),
                    ('LINEBEFORE', (11, 0), (11, -1), 0.50, colors.black),
                    ('LINEBEFORE', (12, 0), (12, -1), 0.50, colors.black),
                    ('LINEBEFORE', (13, 0), (13, -1), 0.50, colors.black),
                    ('LINEBEFORE', (14, 0), (14, -1), 0.50, colors.black),
                    ('LINEAFTER', (14, 0), (14, -1), 0.50, colors.black),
                    ('LINEBELOW', (0, -1), (14, -1), 0.50, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ]))
            # 変数加算
            k+=1

        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 42*mm)

        # 対象年月
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(850, 105, '対象年月：')
        pdf_canvas.drawString(905, 105, search_date[4])

        pdf_canvas.showPage()
