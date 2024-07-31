from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from decimal import Decimal
import math
import datetime

def printstring(pdf_canvas, dt, serch_date):
    # フォント登録
    Yumin = "yumin.ttf"
    pdfmetrics.registerFont(TTFont('游明朝 標準', Yumin))
    #レコード数
    rec = len(dt)
    #行数
    param=30
    #ページ数
    req = math.ceil(rec/param)
    k = 0

    for i in range(req):
        # 集計開始年月日
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(40, 790, serch_date[2])

        # 
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(120, 790, '～')

        # 集計終了年月日
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(145, 790, serch_date[3])

        # 表題
        font_size = 16
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(200, 810, '依頼先別売上順一覧表')

        #ページ数
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        pdf_canvas.drawString(512, 810, str(i+1) + ' ' + '/' + ' ' + str(req) + ' ページ')

        #出力日時
        font_size = 10
        pdf_canvas.setFont('游明朝 標準', font_size)
        time = datetime.datetime.now()
        str_time = time.strftime('%Y年%m月%d日 %H:%M:%S')
        pdf_canvas.drawString(453, 790, str(str_time))

        # テーブルの項目名
        style = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_CENTER)
        itemNo0 = Paragraph('依頼先コード',style)
        itemNo1 = Paragraph('依頼先名',style)
        itemNo2 = Paragraph('売上金額',style)
        itemNo3 = Paragraph('仕入金額',style)
        itemNo4 = Paragraph('粗利金額',style)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4],
        ]
        table = Table(data, colWidths=(30*mm, 70*mm, 30*mm, 30*mm, 30*mm), rowHeights=7.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEABOVE', (0, 0), (-1, 0), 1.00, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 1.00, colors.black),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 265.0*mm)

        data =[]
        Sell=0
        Supplier=0
        Gross=0
        styleLeft = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游明朝 標準', fontSize=9, alignment=TA_RIGHT)

        if i==0:
            k=0
        else:
            k = i*param
        rowlg = (i+1)*param

        while k < rowlg:
            if k<rec:
                RequestCode = Paragraph(dt[k]['OrderingId__RequestCode__CustomerCode'],styleLeft)
                CustomerName = Paragraph(dt[k]['OrderingId__RequestCode__CustomerName'],styleLeft)
                Sell_total = Paragraph(f"{int(dt[k]['Sell_total']):,}",styleRight)
                Supplier_total = Paragraph(f"{int(dt[k]['Supplier_total']):,}",styleRight)
                Profit_total = dt[k]['Sell_total'] - dt[k]['Supplier_total']
                Gross_Profit = Paragraph(f"{int(Profit_total):,}",styleRight)
                # 合計計算
                Sell += Decimal(dt[k]['Sell_total'])
                Supplier += Decimal(dt[k]['Supplier_total'])
                Gross += Decimal(Profit_total)
                data += [
                        [RequestCode, CustomerName, Sell_total, Supplier_total, Gross_Profit],
                ]
            elif i==(req-1) and k==(rowlg-1):
                Sell_total_total = Paragraph(f"{int(Sell):,}",styleRight)
                Supplier_total_total = Paragraph(f"{int(Supplier):,}",styleRight)
                Gross_Profit_total = Paragraph(f"{int(Gross):,}",styleRight)
                data += [
                        ['合計', '', Sell_total_total, Supplier_total_total, Gross_Profit_total],
                ]
            else:
                data += [
                        ['', '', '', '', ''],
                ]

            table = Table(data, colWidths=(30*mm, 70*mm, 30*mm, 30*mm, 30*mm), rowHeights=8.0*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游明朝 標準', 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            k += 1

        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 25*mm)

        pdf_canvas.showPage()