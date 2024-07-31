from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont

# 計算用
from decimal import Decimal
import math

def printstring(pdf_canvas,dt,dt_own):
    #レコード数
    rec = len(dt)
    #行数
    param=10
    #ページ数
    req = math.ceil(rec/param)
    k = 0

    for i in range(req):
        # フォント登録
        YuGosic = "YuGothR.ttc"
        YuGosicB = "YuGothB.ttc"
        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))
        leftmargin = 2
        #width, height = B5
        # 線の太さ
        pdf_canvas.setLineWidth(0.25)

        # title
        font_size = 18
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(308, 470, '発　　注　　書')

        # 注文日
        OrderingDate = dt[0]['OrderingDate'].strftime('%Y年%m月%d日') 
        font_size = 11
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(610, 460, OrderingDate)

        # 発注先
        if str(dt[0]['TitleDiv'])=='0':
            Title=''
        elif str(dt[0]['TitleDiv'])=='1':
            Title='様'
        elif str(dt[0]['TitleDiv'])=='2':
            Title='御中'
        else:
            Title=''

        font_size = 16
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(20, 440, str(dt[0]['DestinationCode__CustomerName']) + '　' + str(dt[0]['SupplierPerson']) + 
                              '　' + str(Title))

        font_size = 11
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(20, 410, '下記のとおり、発注致します。')

        #出荷先
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_LEFT)
        itemNo0 = Paragraph(dt[0]['ShippingCode__CustomerName'],style)
        itemNo1 = Paragraph(dt[0]['ShippingCode__PrefecturesCode__prefecturename'] + dt[0]['ShippingCode__Municipalities'] + 
                            dt[0]['ShippingCode__Address'] + dt[0]['ShippingCode__BuildingName'],style)
        itemNo2 = Paragraph(dt[0]['ShippingCode__PhoneNumber'],style)

        data = [
            ['出荷先', itemNo0],
            ['出荷先住所',itemNo1],
            ['出荷先TEL',itemNo2],
        ]

        table = Table(data, colWidths=(25*mm, 80*mm), rowHeights=5.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 11),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.25,  colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (0, 2), colors.skyblue),
                ('TEXTCOLOR', (0, 0), (0, 2), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 7.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 7.0*mm, 128.0*mm)

        #オーダーNO
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_LEFT)
        itemNo0 = Paragraph(dt[0]['SlipDiv'] + dt[0]['OrderNumber'],style)

        data = [
            ['オーダーNo', itemNo0],
        ]

        table = Table(data, colWidths=(25*mm, 80*mm), rowHeights=5.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 11),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.25,  colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (0, 0), colors.skyblue),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 7.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 7.0*mm, 118.0*mm)

        # 自社名
        font_size = 16
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(485, 390, '株式会社')

        pdfmetrics.registerFont(TTFont('游ゴシック 太字', YuGosicB))
        font_size = 18
        pdf_canvas.setFont('游ゴシック 太字', font_size)
        contents = 'タウ'
        pdf_canvas.drawString(552, 390, contents)
        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))

        # 会社ロゴ
        img = './mysite/myapp/templates/image/image1.jpg'
        #img = './static/image/image1.jpg'
        pdf_canvas.drawImage(img, 207*mm, 135*mm, 45.0*mm, 12.0*mm)

        # 自社情報
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)

        pdf_canvas.drawString(485, 360, '〒 ' + dt_own[0]['PostCode'])
        pdf_canvas.drawString(485, 345, dt_own[0]['PrefecturesCode__prefecturename'] + 
                              dt_own[0]['Municipalities'] + dt_own[0]['Address'] + dt_own[0]['BuildingName'])
        pdf_canvas.drawString(505, 330, 'TEL: ' + dt_own[0]['PhoneNumber'] + '　FAX: ' + dt_own[0]['FaxNumber'])

        # No, 品番、番手、色番、色名、数量、単位、単価、希望納期、回答納期、備考(中央寄せ)
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=10, textColor='white', alignment=TA_CENTER)
        itemNo  = Paragraph('',style)
        itemNo0 = Paragraph('品' + '&nbsp&nbsp' + '番',style)
        itemNo1 = Paragraph('番手',style)
        itemNo2 = Paragraph('色番',style)
        itemNo3 = Paragraph('色' + '&nbsp&nbsp' + '名',style)
        itemNo4 = Paragraph('数量',style)
        itemNo5 = Paragraph('単位',style)
        itemNo6 = Paragraph('単価',style)
        itemNo7 = Paragraph('希望納期',style)
        itemNo8 = Paragraph('回答納期',style)
        itemNo9 = Paragraph('備' + '&nbsp&nbsp&nbsp' + '考',style)

        data = [
             [itemNo, itemNo0, itemNo1, itemNo2, itemNo3, itemNo4, itemNo5, itemNo6, itemNo7, itemNo8, itemNo9],
         ]

        table = Table(data, colWidths=(8*mm, 26*mm, 16*mm, 20*mm, 30*mm, 15*mm, 12*mm, 19*mm, 20*mm, 20*mm, 52*mm), rowHeights=7*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 10),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.25,  colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (-1, -1), colors.skyblue),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 7.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 7.0*mm, 103.0*mm)

        data =[]
        l=len(dt)
        Pname=''
        Ocnt=''
        styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
        styleCenter = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_CENTER)

        if i==0:
            k=0
        else:
            k = i*param
        rowlg = (i+1)*param
        
        while k < rowlg:
            # No
            No = str(k+1)
            Number = Paragraph(No,styleRight)
            if k<l: 
                row = dt[k]
                # 品名（前の行と同一品名の場合は空白）
                if Pname == row['ProductName']:
                    ProductName = ''
                else:
                    ProductName = Paragraph(row['ProductName'],styleCenter)
                # 番手（前の行と同一番手の場合は空白）
                if Ocnt == row['OrderingCount']:
                    OrderingCount = ''
                else:
                    OrderingCount = Paragraph(row['OrderingCount'],styleLeft)
                #色番
                DetailColorNumber = Paragraph(row['OrderingTableId__DetailColorNumber'],styleLeft)
                #カラー
                DetailColor = Paragraph(row['OrderingTableId__DetailColor'],styleLeft)
                #摘要
                DetailSummary = Paragraph(row['OrderingTableId__DetailSummary'],styleLeft)
                #単位
                if str(row['OrderingTableId__DetailUnitDiv'])=='0':
                    Unit=''
                elif str(row['OrderingTableId__DetailUnitDiv'])=='1':
                    Unit='㎏'
                elif str(row['OrderingTableId__DetailUnitDiv'])=='2':
                    Unit='本'
                else:
                    Unit=''
                UnitDiv = Paragraph(Unit,styleCenter)
                #希望納期
                if row['OrderingTableId__StainAnswerDeadline']!=None:
                    Deadline = row['OrderingTableId__StainAnswerDeadline'].strftime('%m/%d') 
                else:
                    Deadline = ''
                StainAnswerDeadline = Paragraph(Deadline,styleRight)
                #回答納期
                if row['OrderingTableId__SpecifyDeliveryDate']!=None:
                    DeliveryDate = row['OrderingTableId__SpecifyDeliveryDate'].strftime('%m/%d') 
                else:
                    DeliveryDate = ''
                SpecifyDeliveryDate = Paragraph(DeliveryDate,styleRight)
                # 指定した列の右寄せ
                # 0なら空白を送る
                if row['OrderingTableId__DetailVolume'] == '0.00':
                    varivol = ' '
                else:
                    varivol = row['OrderingTableId__DetailVolume']
                Volume = Paragraph('{:,.2f}'.format(varivol),styleRight)

                # 0なら空白を送る
                if row['OrderingTableId__DetailUnitPrice'] == '0':
                    variPrice = ' '
                else:
                    variPrice = row['OrderingTableId__DetailUnitPrice']

                UnitPrice = Paragraph('{:,.0f}'.format(variPrice),styleRight)
                # 品名の保存
                Pname = row['ProductName']
                # 番手の保存
                Ocnt = row['OrderingCount']

                data += [
                        [Number, ProductName, OrderingCount, DetailColorNumber, DetailColor, Volume, UnitDiv, UnitPrice, SpecifyDeliveryDate, StainAnswerDeadline, DetailSummary],
                ]
            else:
                data += [
                        [Number, '','','','','','','','','',''],
                ]

            table = Table(data, colWidths=(8*mm, 26*mm, 16*mm, 20*mm, 30*mm, 15*mm, 12*mm, 19*mm, 20*mm, 20*mm, 52*mm), rowHeights=7*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 9),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.dimgray),
                    # 背景色
                    ('BACKGROUND', (0, 1), (10, 1), colors.whitesmoke),
                    ('BACKGROUND', (0, 3), (10, 3), colors.whitesmoke),
                    ('BACKGROUND', (0, 5), (10, 5), colors.whitesmoke),
                    ('BACKGROUND', (0, 7), (10, 7), colors.whitesmoke),
                    ('BACKGROUND', (0, 9), (10, 9), colors.whitesmoke),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]))
            k += 1

        table.wrapOn(pdf_canvas, 7.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 7.0*mm, 33.0*mm)


        #摘要
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=11, alignment=TA_LEFT)

        data = [
            ['摘要'],
            ['出荷次第、オーダーNoを記入した納品書を翌日当社宛にご連絡ください。'],
            [''],
            [''],
        ]

        table = Table(data, colWidths=(238*mm), rowHeights=6*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 10),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgray),
                ('LINEABOVE', (0, 1), (0, 1), 0.50, colors.dimgray),
                # 背景色 先頭
                ('BACKGROUND', (0, 0), (0, 0), colors.skyblue),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        table.wrapOn(pdf_canvas, 7.0*mm, 10*mm)
        table.drawOn(pdf_canvas, 7.0*mm, 5.0*mm)

        pdf_canvas.showPage()