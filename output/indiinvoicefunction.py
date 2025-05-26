from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont

# 日時
import datetime
# 計算用
from decimal import Decimal
import math

def printstring(pdf_canvas,dt,dt_own):
    #レコード数
    rec = len(dt)
    #行数
    param=12
    #ページ数
    req = math.ceil(rec/param)
    k = 0
    page = 0
    total=0
    total_reserve=0

    for i in range(req):
        # フォント登録
        YuGosic = "YuGothR.ttc"
        YuGosicB = "YuGothB.ttc"
        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))
        pdfmetrics.registerFont(TTFont('游ゴシック 太字', YuGosicB))
        # 線の太さ
        pdf_canvas.setLineWidth(0.25)
        # title
        font_size = 20
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(370, 560, '納　品　書')
        # 得意先名
        font_size = 20
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(15, 520, dt[0]['OrderingId__CustomeCode_id__CustomerName'] + '　' + '御中')
        # ページ番号
        #page=i+1
        #font_size = 10
        #pdf_canvas.setFont('HeiseiMin-W3', font_size)
        #pdf_canvas.drawString(550, 820, str(page) + ' / ' + str(req))
        # 発行日
        font_size = 13
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(670, 550, '発行日')
        issuedate = datetime.datetime.strptime(str(dt[0]['IssueDate']), '%Y%m%d')
        Dateofissue = issuedate.strftime('%Y年%m月%d日') 
        font_size = 13
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(730, 550, Dateofissue)
        # 個別請求番号
        font_size = 13
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(670, 530, '伝票番号')
        font_size = 13
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(780, 530, dt[0]['InvoiceNUmber'])
        # 自社情報
        font_size = 13
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(605, 465, '株式会社')

        font_size = 22
        pdf_canvas.setFont('游ゴシック 太字', font_size)
        contents = 'タウ'
        pdf_canvas.drawString(665, 465, contents)

        # 会社ロゴ
        #img = './mysite/myapp/templates/image/image1.jpg'
        img = './static/image/image1.jpg'
        pdf_canvas.drawImage(img, 250*mm, 161*mm, 51.75*mm, 13.8*mm)

        # 自社住所
        font_size = 12
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(580, 420, '〒 ' + dt_own[0]['PostCode'])
        pdf_canvas.drawString(580, 405, dt_own[0]['OwnAddress'])
        pdf_canvas.drawString(604, 390, 'TEL: ' + dt_own[0]['PhoneNumber'] + '　FAX: ' + dt_own[0]['FaxNumber'])
        #取引銀行名
        font_size = 12
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(637, 375, 'みずほ銀行青山支店　普通3258651')
        # 登録番号
        font_size = 12
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(673, 360, '登録番号：T9011201025256')
        # 品名、番手、色番、色名、数量、単位、単価、希望納期、回答納期、備考(中央寄せ)
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=11, textColor='white', alignment=TA_CENTER)
        itemNo0 = Paragraph('出荷日',style)
        itemNo1 = Paragraph('品名／品番',style)
        itemNo2 = Paragraph('番手',style)
        itemNo3 = Paragraph('色番',style)
        itemNo4 = Paragraph('色名',style)
        itemNo5 = Paragraph('数量',style)
        itemNo6 = Paragraph('単位',style)
        itemNo7 = Paragraph('単価',style)
        itemNo8 = Paragraph('金額',style)
        itemNo9 = Paragraph('摘' + '&nbsp&nbsp&nbsp' + '要',style)
        data = [
            [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8, itemNo9],
        ]
        table = Table(data, colWidths=(20.0*mm, 56.0*mm, 20.0*mm, 26.0*mm, 50.0*mm, 18*mm, 15*mm, 25*mm, 25*mm, 33*mm), rowHeights=8.0*mm)

        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 11),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.25,  colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#87CAD7")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 4.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 4.0*mm, 114.0*mm)

        data =[]
        l=len(dt)
        #total=0
        styleLeftmin = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_LEFT)
        styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_RIGHT)
        styleCenter = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_CENTER)

        if i==0:
            k=0
        else:
            k = i*param
        rowlg = (i+1)*param
        
        while k < rowlg:
            if k<l:
                row = dt[k]
                # 合計計算
                total += int(Decimal(row['SellPrice']))
                #出荷日
                if row['ShippingDate']!=None:
                    ShippDate = row['ShippingDate'].strftime('%m/%d') 
                else:
                    ShippDate = ''

                ShippingDate = Paragraph(ShippDate,styleCenter)
                # 品名
                if len(row['OrderingId__ProductName']) > 10:
                    ProductName = Paragraph(row['OrderingId__ProductName'],styleLeftmin)
                else:
                    ProductName = Paragraph(row['OrderingId__ProductName'],styleLeft)
                # 品番
                ColorNumber = Paragraph(row['OrderingDetailId__DetailColorNumber'],styleLeft)
                # 番手
                OrderingCount = Paragraph(row['OrderingId__OrderingCount'],styleLeft)
                # カラー
                DetailColor = Paragraph(row['OrderingDetailId__DetailColor'],styleLeft)
                # 単価
                DetailSellPrice = Paragraph('{:,.0f}'.format(row['OrderingDetailId__DetailSellPrice']),styleRight)
                #単位
                if str(row['OrderingDetailId__DetailUnitDiv'])=='0':
                    Unit=''
                elif str(row['OrderingDetailId__DetailUnitDiv'])=='1':
                    Unit='㎏'
                elif str(row['OrderingDetailId__DetailUnitDiv'])=='2':
                    Unit='本'
                elif str(row['OrderingDetailId__DetailUnitDiv'])=='3':
                    Unit='枚'
                elif str(row['OrderingDetailId__DetailUnitDiv'])=='4':
                    Unit='件'
                else:
                    Unit=''
                DetailUnitDiv = Paragraph(Unit,styleCenter)
                #摘要
                ResultSummary = Paragraph(row['ResultSummary'],styleLeft)
                #オーダーNO
                OrderNumber = row['OrderNumber']

                #数量(0なら空白を送る)
                if row['ShippingVolume'] == '0.00':
                    varivol = ' '
                else:
                    varivol = row['ShippingVolume']
                ShippingVolume = Paragraph('{:,.2f}'.format(varivol),styleRight)
                #金額(0なら空白を送る)
                if row['SellPrice'] == '0':
                    variPrice = ' '
                else:
                    #variPrice = row['SellPrice']
                    #2024-10-25 不具合発生により変更
                    variPrice = int(row['SellPrice'])

                SellPrice = Paragraph('{:,.0f}'.format(variPrice),styleRight)

                data += [
                        [ShippingDate, ProductName, OrderingCount, ColorNumber,   DetailColor, ShippingVolume, DetailUnitDiv, DetailSellPrice, SellPrice, ResultSummary],
                ]
            else:
                data += [
                        ['','','','','','','','','',''],
                ]

            table = Table(data, colWidths=(20.0*mm, 56.0*mm, 20.0*mm, 26.0*mm, 50.0*mm, 18*mm, 15*mm, 25*mm, 25*mm, 33*mm), rowHeights=8.0*mm)
            table.setStyle(TableStyle([
                    ('LINEBEFORE', (0, 0), (0, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (1, 0), (1, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (2, 0), (2, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (3, 0), (3, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (4, 0), (4, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (5, 0), (5, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (6, 0), (6, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (7, 0), (7, 11), 0.25, colors.dimgray),
                    ('LINEBEFORE', (8, 0), (8, 11), 0.25, colors.dimgray),
                    ('LINEAFTER' , (8, 0), (8, 11), 0.25, colors.dimgray),
                    ('LINEAFTER' , (9, 0), (9, 11), 0.25, colors.dimgray),
                    ('LINEBELOW' , (0, 0), (9, 7), 0.25, colors.dimgray),
                    ('LINEBELOW' , (0, 8), (9, 10), 0.25, colors.dimgray),
                    ('LINEBELOW' , (0, 11), (6, 11), 0.25, colors.dimgray),
                    # 背景色
                    ('BACKGROUND', (0, 1), (9, 1), colors.whitesmoke),
                    ('BACKGROUND', (0, 3), (9, 3), colors.whitesmoke),
                    ('BACKGROUND', (0, 5), (9, 5), colors.whitesmoke),
                    ('BACKGROUND', (0, 7), (9, 7), colors.whitesmoke),
                    ('BACKGROUND', (0, 9), (9, 9), colors.whitesmoke),
                    ('BACKGROUND', (0, 11), (11, 11), colors.whitesmoke),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]))
            # 変数加算
            k += 1

        table.wrapOn(pdf_canvas, 4.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 4.0*mm, 18.0*mm)

        #合計
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=11, textColor='white', alignment=TA_RIGHT)
        if str(i) == str(req - 1): 
            itemNo10 = Paragraph('税抜合計',style)
            itemNo11 = Paragraph(str(f"{int(total):,}"),styleRight)
        else:
            itemNo10 = Paragraph('',styleRight)
            itemNo11 = Paragraph(str(''),styleRight)

        data = [
            [itemNo10, itemNo11,''],
        ]

        table = Table(data, colWidths=(25*mm, 25*mm, 33*mm), rowHeights=8.0*mm)
        table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('LINEBEFORE', (1, 0), (2, 0), 0.25, colors.dimgray),
                # 背景色
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#87CAD7")),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 209.0*mm, 10.0*mm)
        #オーダーNO
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=12, alignment=TA_LEFT)
        contents = Paragraph(OrderNumber,style)

        data = [
            ['オーダーNo', contents],
        ]

        table = Table(data, colWidths=(30*mm, 70*mm), rowHeights=6.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 12),
                ('FONT', (0, 0), (1, 0), '游ゴシック 太字', 12),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.25,  colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#87CAD7")),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 5.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 5.0*mm, 130.0*mm)

        pdf_canvas.showPage()
