from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont

def printstring(pdf_canvas, dt, dt_Prev, i, width, serch_date):
    # フォント登録
    Yumin = "yumin.ttf"
    pdfmetrics.registerFont(TTFont('游明朝 標準', Yumin))
    if i % 25 == 0 or i % 50 == 0:
        # 集計開始年月日
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 660, serch_date[4])

        # 
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(120, 660, '～')

        # 集計終了年月日
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(145, 660, serch_date[5])

        # 表題
        font_size = 16
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(400, 670, '得意先月次集計表')

         # 押印欄
        style = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)
        data = [
            ['係','','',''],
            ['印','','',''],
        ]
        table = Table(data, colWidths=(5*mm, 15*mm, 5*mm, 15*mm), rowHeights=9.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.black),
                ('LINEBEFORE', (0, 0), (1, 1), 0.50, colors.black),
                ('LINEBEFORE', (2, 0), (2, 1), 0.50, colors.black),
                ('LINEBEFORE', (3, 0), (3, 1), 0.50, colors.black),
                ('VALIGN', (0, 0), (0, 1), 'TOP'),
                ('VALIGN', (1, 0), (1, 1), 'BOTTOM'),
                ('ALIGN', (0, 0), (1, 1), 'CENTER'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 300*mm, 230.0*mm)

        # テーブルの項目名
        style = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)
        itemNo0 = Paragraph('得意先コード',style)
        itemNo1 = Paragraph('得意先名',style)
        itemNo2 = Paragraph('前月繰越額',style)
        itemNo3 = Paragraph('売上金額',style)
        itemNo4 = Paragraph('消費税額',style)
        itemNo5 = Paragraph('税込売上金額',style)
        itemNo6 = Paragraph('入金金額',style)
        itemNo7 = Paragraph('次月繰越額',style)
        itemNo8 = Paragraph('済',style)
        itemNo9 = Paragraph('備考',style)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8, itemNo9],
        ]
        table = Table(data, colWidths=(30*mm, 60*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 10*mm, 50*mm), rowHeights=8.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.50,  colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 220.0*mm)

    data =[]
    l=len(dt)
    styleLeft = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_LEFT)
    styleRight = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_RIGHT)

    k=0
    while k < l:
        row = dt_Prev
        CustomerCode = Paragraph(dt[k]['CustomerCode'],styleLeft)
        CustomerName = Paragraph(dt[k]['CustomerName'],styleLeft)
        PrevBill = Paragraph(f"{int(row[0]):,}",styleRight)
        Sell = Paragraph(f"{int(row[3]):,}",styleRight)
        Tax = Paragraph(f"{int(row[4]):,}",styleRight)
        Total = row[3] + row[4]
        SellTotal = Paragraph(f"{int(Total):,}",styleRight)
        Deposit = Paragraph(f"{int(row[1]):,}",styleRight)
        Carryover = Paragraph(f"{int(row[5]):,}",styleRight)

        data += [
                [CustomerCode, CustomerName, PrevBill, Sell, Tax, SellTotal, Deposit, Carryover, '', ''],
        ]

        table = Table(data, colWidths=(30*mm, 60*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 10*mm, 50*mm), rowHeights=8.0*mm)
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
                ('LINEAFTER', (9, 0), (9, -1), 0.50, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, width*mm)
        # 変数加算
        k+=1

def blankprintstring(pdf_canvas, width):
    data = [
            ['', '', '', '', '', '', '', '', '', ''],
    ]

    table = Table(data, colWidths=(30*mm, 60*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 10*mm, 50*mm), rowHeights=8.0*mm)
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
            ('LINEAFTER', (9, 0), (9, -1), 0.50, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 10*mm, 10*mm)
    table.drawOn(pdf_canvas, 10*mm, width*mm)

def totalprintstring(pdf_canvas, width, total):
    styleCenter = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)
    styleRight = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_RIGHT)

    strtotal = Paragraph('合&nbsp;&nbsp;計',styleCenter)
    BillTotal = Paragraph(f"{int(total[0]):,}",styleRight)
    SellTotal = Paragraph(f"{int(total[1]):,}",styleRight)
    TaxTotal = Paragraph(f"{int(total[2]):,}",styleRight)
    SellTaxTotal = Paragraph(f"{int(total[3]):,}",styleRight)
    DepositTotal = Paragraph(f"{int(total[4]):,}",styleRight)
    CarryoverTotal = Paragraph(f"{int(total[5]):,}",styleRight)
    data = [
            [strtotal, '', BillTotal, SellTotal, TaxTotal, SellTaxTotal, DepositTotal, CarryoverTotal, '', ''],
    ]

    table = Table(data, colWidths=(30*mm, 60*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 10*mm, 50*mm), rowHeights=8.0*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
            ('BOX', (0, 0), (-1, -1), 0.50, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.50,  colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 10*mm, 10*mm)
    table.drawOn(pdf_canvas, 10*mm, width*mm)

def lineprintstring(pdf_canvas):
    data = [['', '', '', '', '', '', '', '', '', ''],]

    table = Table(data, colWidths=(30*mm, 60*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 30*mm, 10*mm, 50*mm), rowHeights=0.1*mm)
    table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 0.50, colors.black),
        ]))
    table.wrapOn(pdf_canvas, 10*mm, 10*mm)
    table.drawOn(pdf_canvas, 10*mm, 20*mm)

