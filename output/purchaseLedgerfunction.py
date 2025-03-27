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

def printstring(pdf_canvas, dt, dt_Prev, dt_Detail, PrtDate, CurryDate):
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
        pdf_canvas.drawString(420, 670, '仕　入　台　帳')

        # 仕入先名
        Supplier_Name = dt[0]['CustomerCode'] + ' ' + dt[0]['CustomerName']
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 640, Supplier_Name[1:20])
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
        itemNo1 = Paragraph('伝票NO',style)
        itemNo2 = Paragraph('出荷日',style)
        itemNo3 = Paragraph('依頼NO',style)
        itemNo4 = Paragraph('商品名',style)
        itemNo5 = Paragraph('番手',style)
        itemNo6 = Paragraph('数量',style)
        itemNo7 = Paragraph('単価',style)
        itemNo8 = Paragraph('課税仕入額',style)
        itemNo10 = Paragraph('消費税額',style)
        itemNo13 = Paragraph('非課税仕入額',style)
        itemNo11 = Paragraph('前月繰越額',style)
        itemNo12 = Paragraph('支払金額',style)
        itemNo14 = Paragraph('差引金額',style)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8, itemNo10, itemNo13, itemNo11, itemNo12, itemNo14],
        ]
        table = Table(data, colWidths=(22*mm, 20*mm, 22*mm, 20*mm, 47*mm, 18*mm, 18*mm, 20*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm), rowHeights=8.0*mm)
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
                    [CurryDate, '', '', '', ProductName, '', '', '', '', '', '', PrevBill, '', PrevBill],
            ]
        else:
            data = [
                    ['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ]

        table = Table(data, colWidths=(22*mm, 20*mm, 22*mm, 20*mm, 47*mm, 18*mm, 18*mm, 20*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm), rowHeights=8.0*mm)
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
                ('LINEAFTER', (13, 0), (13, -1), 0.50, colors.black),
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
            item5=0
            Adjustment=0

        while k < rowlg:
            if k<rec and len(dt_Detail)>0:
                row = dt_Detail[k]
                #年月日
                startdate = row['InvoiceIssueDate'].strftime('%Y/%m/%d')
                InvoiceIssueDate = Paragraph(startdate,styleLeft)

                #伝票NO、番手
                SlipNo = Paragraph(row['SlipNumber'],styleRight)
                OrderingCount = Paragraph(row['OrderingCount'],styleLeft)

                #出荷日
                if row['Division']=='1' or row['Division']=='1.5':
                    ShippDate = row['ShippingDate'].strftime('%Y/%m/%d')
                    ShippingDate = Paragraph(ShippDate,styleLeft)
                elif row['Division']=='2':
                    ShippingDate = Paragraph('',styleLeft)
                else:
                    ShippingDate = Paragraph('',styleLeft)

                #商品名
                ProductName = Paragraph(row['ProductName'],styleLeft)

                #オーダーNO(依頼NO)
                if row['Division']=='1' or row['Division']=='1.5':
                    OrderNumber = Paragraph(row['SlipDiv_Max']+'-'+row['OrderNumber'],styleLeft)
                else:
                    OrderNumber = Paragraph('',styleLeft)

                #数量
                if row['Division']=='1' or row['Division']=='1.5':
                    ShippingVol = Paragraph('{:,.2f}'.format(row['Shipping_total']),styleRight)
                else:
                    ShippingVol = Paragraph('',styleRight)

                #単価
                if row['Division']=='1' or row['Division']=='1.5':
                    if int(row['DetailUnitPrice'])!=0:
                        StockPrice = Paragraph(f"{int(row['DetailUnitPrice']):,}",styleRight)
                    else:
                        StockPrice = Paragraph('',styleRight)
                else:
                    StockPrice = Paragraph('',styleRight)

                #仕入金額,非課税仕入金額
                # if row['Division']=='1' or row['Division']=='1.5':
                #     if int(row['Abs_total'])!=0:
                #         StockTotal = Paragraph(f"{int(row['Abs_total']):,}",styleRight)
                #     else:
                #         StockTotal = Paragraph('',styleRight)
                #     item1 += int(row['Abs_total'])
                #     if row['Division']=='1.5':
                #         item5+=int(row['Abs_total'])
                # else:
                #     StockTotal = Paragraph('',styleRight)

                if row['Division']=='1' and int(row['Abs_total'])!=0:
                    StockTotal = Paragraph(f"{int(row['Abs_total']):,}",styleRight)
                    item1+=int(row['Abs_total'])
                else:
                    StockTotal = Paragraph('',styleRight)

                if row['Division']=='1.5' and int(row['Abs_total'])!=0:
                    TaxExempt = Paragraph(f"{int(row['Abs_total']):,}",styleRight)
                    item5+=int(row['Abs_total'])
                else:
                    TaxExempt = Paragraph('',styleRight)

                #支払額,摘要
                if row['Division']=='1':
                    Summary = Paragraph('',styleLeft)
                    Pay = Paragraph('',styleRight)
                elif row['Division']=='2':
                    Summary = Paragraph(row['Summary'],styleLeft)
                    Pay = Paragraph(f"{int(row['SlipDiv']):,}",styleRight)
                    item2 += Decimal(row['SlipDiv'])
                else:
                    Summary = Paragraph('',styleLeft)
                    Pay = Paragraph('',styleRight)

                #前回繰越額
                if row['Division']=='1' or row['Division']=='1.5':
                    item += int(row['Abs_total'])
                elif row['Division']=='2':
                    item -= Decimal(row['SlipDiv'])

                #消費税調整
                if row['Division']=='3':
                    Adjust = Paragraph(f"{int(row['Detailsellprice']):,}",styleRight)
                    Adjustment += int(row['Detailsellprice'])
                else:
                    Adjust = Paragraph('',styleRight)

                Deduction = Paragraph(f"{int(item):,}",styleRight)
                data += [
                        [InvoiceIssueDate, SlipNo, ShippingDate, OrderNumber, ProductName, OrderingCount, ShippingVol, StockPrice, StockTotal,
                         Adjust, TaxExempt, Pay, Summary, Deduction],
                ]
            elif k==(rowlg-1) and t==(req-1):
                #最終行
                #課税仕入金額合計
                if item1==0:
                    StockPriceTotal = Paragraph('',styleRight)
                else:
                    StockPriceTotal = Paragraph(f"{int(item1):,}",styleRight)
                #前回繰越額
                PrvBillTotal = Paragraph(f"{int(dt_Prev[0]):,}",styleRight)
                #支払額合計
                if item2==0:
                    PayTotal = Paragraph('',styleRight)
                else:
                    PayTotal = Paragraph(f"{int(item2):,}",styleRight)

                #合計消費税額
                #item3 = int((item1 - item5) * 0.1) + int(Adjustment)
                item3 = int(item1 * 0.1) + int(Adjustment)
                if item3==0:
                    TaxTotal = Paragraph('',styleRight)
                else:
                    TaxTotal = Paragraph(f"{int(item3):,}",styleRight)

                #非課税仕入金額合計
                if item5==0:
                    TaxexemptTotal = Paragraph('',styleRight)
                else:
                    TaxexemptTotal = Paragraph(f"{int(item5):,}",styleRight)

                #次回繰越額
                item4 = int(item + item3)
                Total = Paragraph(f"{int(item4):,}",styleRight)

                data += [
                        ['', '', '', '', '', '', '', '', StockPriceTotal, TaxTotal, TaxexemptTotal, PrvBillTotal, PayTotal, Total],
                ]
            else:
                data += [
                        ['', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                ]

            table = Table(data, colWidths=(22*mm, 20*mm, 22*mm, 20*mm, 47*mm, 18*mm, 18*mm, 20*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm, 25*mm), rowHeights=8.0*mm)
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
                    ('LINEAFTER', (13, 0), (13, -1), 0.50, colors.black),
                    ('LINEBELOW', (0, -1), (13, -1), 0.50, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ]))
            # 変数加算
            k+=1

        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 42*mm)

        # 対象年月
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(880, 105, '対象年月：')
        pdf_canvas.drawString(932, 105, PrtDate)

        pdf_canvas.showPage()
