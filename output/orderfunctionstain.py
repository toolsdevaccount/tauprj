from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import dimgrey
# 計算用
from decimal import Decimal
import math

def printstringStainRequest(pdf_canvas,dt,dt_own):
    #レコード数
    rec = len(dt)
    #行数
    param=11
    #ページ数
    req = math.ceil(rec/param)
    k = 0

    for i in range(req):
        # フォント登録
        YuGosic = "YuGothR.ttc"
        YuGosicB = "YuGothB.ttc"
        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))

        # 線の太さ
        pdf_canvas.setLineWidth(0.25)

        # title
        font_size = 16
        pdf_canvas.setFont('游ゴシック 標準', font_size)

        if dt[0]['OutputDiv']==2:
            pdf_canvas.drawString(250, 810, '染 付 依 頼 書')
        if dt[0]['OutputDiv']==3:
            pdf_canvas.drawString(200, 810, 'ビ ー カ ー 染 付 依 頼 書')

        # 依頼日
        font_size = 11
        OrderingDate = dt[0]['OrderingDate'].strftime('%Y年%m月%d日') 
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(480, 790, OrderingDate)

        # 発注先
        if str(dt[0]['TitleDiv'])=='0':
            Title=''
        elif str(dt[0]['TitleDiv'])=='1':
            Title='様'
        elif str(dt[0]['TitleDiv'])=='2':
            Title='御中'
        else:
            Title=''
        font_size = 14
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(43, 760, dt[0]['DestinationCode__CustomerName'] + '　' + dt[0]['SupplierPerson'] + Title)

        # 自社情報
        font_size = 12
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(357, 740, '株式会社')

        pdfmetrics.registerFont(TTFont('游ゴシック 太字', YuGosicB))
        font_size = 18
        pdf_canvas.setFont('游ゴシック 太字', font_size)
        contents = 'タウ'
        pdf_canvas.drawString(410, 740, contents)

        # ロゴ追加
        #img = './mysite/myapp/templates/image/image1.jpg'
        img = './static/image/image1.jpg'
        pdf_canvas.drawImage(img, 165*mm, 258*mm, 45.0*mm, 12.0*mm)

        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(357, 720, '〒 ' + dt_own[0]['PostCode'])
        pdf_canvas.drawString(357, 710, dt_own[0]['PrefecturesCode__prefecturename'] + dt_own[0]['Municipalities'] + dt_own[0]['Address'] + dt_own[0]['BuildingName'])
        pdf_canvas.drawString(385, 700, 'TEL: ' + dt_own[0]['PhoneNumber'] + ' FAX: ' + dt_own[0]['FaxNumber'])

        # メッセージ
        font_size = 9
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(23, 700,'下記の通りご依頼致します。')

        # line 
        pdf_canvas.setStrokeColor(dimgrey)
        pdf_canvas.line(20, 690, 570, 690) 
        pdf_canvas.line(300, 505, 300, 690) 

        # 原糸メーカー
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 680,'原糸メーカー')
        pdf_canvas.drawString(80, 665, dt[0]['StainShippingCode__CustomerName'])
        # Line
        pdf_canvas.line(20, 660, 570, 660) 

        # 原糸出荷
        if dt[0]['StainShippingDate']!=None:
            ShippingDate = dt[0]['StainShippingDate'].strftime('%Y年%m月%d日') 
        else:
            ShippingDate = ''

        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 650,'原糸出荷')
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(80, 635, ShippingDate)
        # Line
        pdf_canvas.line(20, 630, 570, 630) 

        # 品番
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 620,'品番')
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(80, 605, dt[0]['StainPartNumber'])
        # Line
        pdf_canvas.line(20, 600, 570, 600) 

        # 品名
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 590,'品名')
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(80, 575, dt[0]['ProductName'])
        # Line
        pdf_canvas.line(20, 570, 570, 570) 

        # 番手
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 560,'番手')
        pdf_canvas.drawString(80, 545, dt[0]['OrderingCount'])
        # Line
        pdf_canvas.line(20, 540, 570, 540) 

        # 混率
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(25, 530,'混率')
        pdf_canvas.drawString(80, 515, dt[0]['StainMixRatio'])

        # Line
        pdf_canvas.line(20, 505, 570, 505) 

        # オーダーNO
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(305, 680,'オーダーNO')

        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(365, 665, dt[0]['SlipDiv'] + '-' + dt[0]['OrderNumber'])

        # アパレル
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(305, 620,'アパレル')
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(365, 605, dt[0]['ApparelCode__CustomerName'])

        # 出荷先名
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(305, 590,'出荷先')
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(365, 575, dt[0]['ShippingCode__CustomerName'])

        # 出荷先住所
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(305, 560, '〒 ' + dt[0]['ShippingCode__PostCode']) 
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(365, 560, dt[0]['ShippingCode__PrefecturesCode__prefecturename'] + 
                              dt[0]['ShippingCode__Municipalities'] + dt[0]['ShippingCode__Address'] + 
                              dt[0]['ShippingCode__BuildingName']
                              )

        # 出荷先TEL
        font_size = 10
        pdf_canvas.setFont('游ゴシック 標準', font_size)
        pdf_canvas.drawString(365, 545, 'TEL:' + dt[0]['ShippingCode__PhoneNumber'])

        # 項番、色番、カラー、仕立、数量、単価、希望納期、回答納期、摘要
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=9, textColor='white', alignment=TA_CENTER)
        itemNo0 = Paragraph('項番',style)
        itemNo1 = Paragraph('色番',style)
        itemNo2 = Paragraph('色' + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '名',style)
        itemNo4 = Paragraph('数量',style)
        itemNo5 = Paragraph('単価',style)
        itemNo7 = Paragraph('納期',style)
        itemNo8 = Paragraph('回答',style)
        itemNo6 = Paragraph('備' + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '考',style)

        data = [
            [itemNo0, itemNo1, itemNo2, itemNo4, itemNo5, itemNo7, itemNo8, itemNo6] ,
        ]
        data += [
            ['', '', '', '', '', '', '', ''] ,
        ]

        table = Table(data, colWidths=(12*mm, 30*mm, 40*mm, 16*mm, 16*mm, 16*mm, 16*mm, 50*mm), rowHeights=7.5*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 9),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#87CAD7")),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgrey),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.dimgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (1, 0), (1, 1)),
                ('SPAN', (2, 0), (2, 1)),
                ('SPAN', (3, 0), (3, 1)),
                ('SPAN', (4, 0), (4, 1)),
                ('SPAN', (5, 0), (5, 1)),
                ('SPAN', (6, 0), (6, 1)),
                ('SPAN', (7, 0), (7, 1)),
            ]))
        table.wrapOn(pdf_canvas, 7*mm, 10*mm)
        table.drawOn(pdf_canvas, 7*mm, 153.0*mm)

        data =[]
        l=len(dt)
        total=0
        styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
        styleCenter = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_CENTER)

        if i==0:
            k=0
        else:
            k = i*param
        rowlg = (i+1)*param
        
        while k < rowlg:
            if k<l: 
                row = dt[k]
                #数量合計
                total += Decimal(row['OrderingTableId__DetailVolume'])
                #項番
                DetailItemNumber = Paragraph(row['OrderingTableId__DetailItemNumber'],styleCenter)
                #色番
                DetailColorNumber = Paragraph(row['OrderingTableId__DetailColorNumber'],styleLeft)
                #カラー
                DetailColor = Paragraph(row['OrderingTableId__DetailColor'],styleLeft)
                #摘要
                DetailSummary = Paragraph(row['OrderingTableId__DetailSummary'],styleLeft)
                #数量(0なら空白を送る)
                if row['OrderingTableId__DetailVolume'] == '0.00':
                    varivol = ' '
                else:
                    varivol = row['OrderingTableId__DetailVolume']
                Volume = Paragraph('{:,.2f}'.format(varivol),styleRight)
                #単価(0なら空白を送る)
                if row['OrderingTableId__DetailUnitPrice'] == '0':
                    variprice = ' '
                else:
                    variprice = row['OrderingTableId__DetailUnitPrice']

                DetailUnitPrice = Paragraph('{:,.0f}'.format(variprice),styleRight)
                #希望納期
                if row['OrderingTableId__SpecifyDeliveryDate']!=None:
                    Deadline = row['OrderingTableId__SpecifyDeliveryDate'].strftime('%m/%d') 
                else:
                    Deadline = ''
                StainAnswerDeadline = Paragraph(Deadline,styleCenter)
                #回答納期
                if row['OrderingTableId__StainAnswerDeadline']!=None:
                    DeliveryDate = row['OrderingTableId__StainAnswerDeadline'].strftime('%m/%d') 
                else:
                    DeliveryDate = ''
                SpecifyDeliveryDate = Paragraph(DeliveryDate,styleCenter)            
                data += [
                        [DetailItemNumber, DetailColorNumber, DetailColor, Volume, DetailUnitPrice, StainAnswerDeadline, SpecifyDeliveryDate, DetailSummary],
                ]
            else:
                if k==10:
                    # 指定した列の右寄せ
                    if str(total) == '0.00':
                        total = ''
                    
                    Detailtotal = Paragraph(str(total),styleRight)
                    label1= Paragraph(str('合&nbsp;&nbsp;&nbsp;&nbsp;'),styleRight)
                    label2= Paragraph(str('&nbsp;&nbsp;&nbsp;&nbsp;計'),styleLeft)
                    data += [
                            ['', label1, label2, Detailtotal, '', '', ''],
                    ]
                else:            
                    data += [
                            ['','','','','','',''],
                    ]

            table = Table(data, colWidths=(12*mm, 30*mm, 40*mm, 16*mm, 16*mm, 16*mm, 16*mm, 50*mm), rowHeights=12.0*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 8),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgrey),
                    ('INNERGRID', (0, 0), (8, 9), 0.25, colors.dimgrey),
                    ('LINEABOVE', (0, 10), (8, 10), 0.25, colors.dimgrey),
                    ('INNERGRID', (3, 10), (4, 10), 0.25, colors.dimgrey),
                    ('INNERGRID', (2, 10), (3, 10), 0.25, colors.dimgrey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (1, 10), (2, 10), 5),
                ]))
            k += 1

        table.wrapOn(pdf_canvas, 7*mm, 10*mm)
        table.drawOn(pdf_canvas, 7*mm, 21.0*mm)

        pdf_canvas.showPage()