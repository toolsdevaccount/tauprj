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
import math

def printstring(pdf_canvas, dt_own, dt, billdate, dt_Prev, dt_Detail, Date_From):
    #レコード数
    rec = len(dt_Detail)
    if rec==0:
        rec=1
    #行数
    param=31
    #ページ数
    req = math.ceil(rec/param)
    k = 0

    DateFrom=''
    ResultDate=''
    for i in range(req):
        # フォント登録
        YuGosic = "YuGothR.ttc"
        YuGosicB = "YuGothB.ttc"
        pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))
        pdfmetrics.registerFont(TTFont('游ゴシック 太字', YuGosicB))
        # title
        font_size = 18
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(260, 820, '請　求　書')
        # 請求先
        font_size = 12
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(30, 795, '〒 ' + dt[0]['PostCode'])
        pdf_canvas.drawString(30, 780, dt[0]['PrefecturesCode__prefecturename'] + dt[0]['Municipalities'] + dt[0]['Address'])
        pdf_canvas.drawString(60, 760, dt[0]['BuildingName'])
        font_size = 14
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(30, 740, dt[0]['CustomerName'] + '　' + '御中')

        match dt[0]['ClosingDate']:
            case 0:
                Closing=''
            case 5:
                Closing='5日'
            case 10:
                Closing='10日'
            case 15:
                Closing='15日'
            case 20:
                Closing='20日'
            case 25:
                Closing='25日'
            case 31:
                Closing='末日'
            case _:
                Closing=''

        data =[['締日','請求日'],
            [Closing,billdate],
            ]

        table = Table(data, colWidths=(15*mm, 30*mm), rowHeights=(4*mm, 6*mm))
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準',9),
                ('FONT', (0, 0), (1, 0), '游ゴシック 太字', 9),
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#87CAD7")),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.50,  colors.dimgray),
                ('VALIGN', (0, 1), (1, 1), 'MIDDLE'),
                ('ALIGN', (0, 0), (1, -1), 'CENTER'),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 157*mm, 280.0*mm)

        # 自社情報
        # 自社名
        font_size = 10
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(390, 745, '株式会社')

        font_size = 18
        pdf_canvas.setFont('游ゴシック 太字', font_size)
        contents = 'タウ'
        pdf_canvas.drawString(435, 745, contents)
        # 会社ロゴ
        #img = './mysite/myapp/templates/image/image1.jpg'
        img = './static/image/image1.jpg'
        pdf_canvas.drawImage(img, 167*mm, 260*mm, 47.0*mm, 12.0*mm)

        # 自社住所
        font_size = 10
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(366, 730, '〒 ' + dt_own[0]['PostCode'])
        pdf_canvas.drawString(366, 720, dt_own[0]['PrefecturesCode__prefecturename'] + dt_own[0]['Municipalities'] + 
                            dt_own[0]['Address'] + dt_own[0]['BuildingName'])
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(393, 710, 'TEL: ' + dt_own[0]['PhoneNumber'] + ' FAX: ' + dt_own[0]['FaxNumber'])
        #取引銀行名
        font_size = 9
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(393, 700, '取引銀行：みずほ銀行青山支店 普通3258651')
        # 登録番号
        font_size = 9
        pdf_canvas.setFont("游ゴシック 標準", font_size)
        pdf_canvas.drawString(458, 690, '登録番号：T9011201025256')

        # 残高(1ページ目とそれ以降処理分岐)
        if i==0:
            styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
            itemNo10 = Paragraph(f"{int(dt_Prev[0]):,}",styleRight)
            itemNo11 = Paragraph(f"{int(dt_Prev[1]):,}",styleRight)
            itemNo12 = Paragraph(f"{int(dt_Prev[2]):,}",styleRight)
            itemNo13 = Paragraph(f"{int(dt_Prev[3]):,}",styleRight)
            itemNo14 = Paragraph(f"{int(dt_Prev[4]):,}",styleRight)
        else:
            styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
            itemNo10 = Paragraph('*',styleRight)
            itemNo11 = Paragraph('*',styleRight)
            itemNo12 = Paragraph('*',styleRight)
            itemNo13 = Paragraph('*',styleRight)
            itemNo14 = Paragraph('*',styleRight)

        data =[['前回請求額','ご入金額','繰越額','当月税抜ご請求額','消費税額 10%'],
            [itemNo10, itemNo11, itemNo12, itemNo13, itemNo14],]

        table = Table(data, colWidths=(28*mm, 28*mm, 28*mm, 35*mm, 28*mm), rowHeights=(5*mm, 7*mm))
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 太字', 9),
                ('BACKGROUND', (0, 0), (4, 0), colors.HexColor("#87CAD7")),
                ('TEXTCOLOR', (0, 0), (4, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ('ALIGN', (0, 0), (5, 0), 'CENTER'),
                ('VALIGN', (0, 0), (5, 0), 'MIDDLE'),
                ('VALIGN', (0, 1), (5, 1), 'BOTTOM'),
                ('ALIGN', (0, 1), (5, 1), 'RIGHT'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 227.0*mm)

        # 当月税込請求額(1ページ目とそれ以降処理分岐)
        if i==0:
            itemNo15 = Paragraph(f"{int(dt_Prev[5]):,}",styleRight)
        else:
            itemNo15 = Paragraph('*',styleRight)

        data =[['当月税込御請求額'],
            [itemNo15],
            ]

        table = Table(data, colWidths=(35*mm), rowHeights=(5*mm, 7*mm))
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, 0), '游ゴシック 太字', 9),
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#87CAD7")),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('VALIGN', (0, 1), (0, 1), 'BOTTOM'),
                ('ALIGN', (0, 1), (5, 1), 'RIGHT'),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 168*mm, 227.0*mm)

        # 表題
        style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=9, textColor='white', alignment=TA_CENTER)
        itemNo0 = Paragraph('年月日',style)
        itemNo1 = Paragraph('伝票番号',style)
        itemNo3 = Paragraph('品' + '&nbsp;&nbsp;'+ '&nbsp;&nbsp;' + '&nbsp;&nbsp;' + '名',style)
        itemNo4 = Paragraph('数' + '&nbsp;&nbsp;' + '量',style)
        itemNo6 = Paragraph('税抜金額',style)
        itemNo7 = Paragraph('摘' + '&nbsp;&nbsp;' + '要',style)
        data = [
            [itemNo0, itemNo1, itemNo3, '', itemNo4, itemNo6, itemNo7],
        ]
        table = Table(data, colWidths=(18*mm, 18*mm, 61*mm, 20*mm, 21*mm, 25*mm, 30*mm), rowHeights=6.5*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 10),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#87CAD7")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('SPAN', (2, 0), (3, 0)),
            ]))
        table.wrapOn(pdf_canvas, 10*mm, 10*mm)
        table.drawOn(pdf_canvas, 10*mm, 214.0*mm)

        data =[]
        l=len(dt_Detail)
        styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_LEFT)
        styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
        styleCenter = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_CENTER)

        #繰越(1ページ目とそれ以降処理分岐)
        if i==0:
            DateFrom = datetime.datetime.strptime(Date_From, '%Y-%m-%d') 
            ResultDate = Paragraph(DateFrom.strftime('%y%m%d'),styleCenter)
            InvoiceNumber = Paragraph('',styleCenter)
            ProductName = Paragraph('繰越',styleLeft)
            ShippingVolume = Paragraph('',styleRight)      
            Prceeds = Paragraph(f"{int(dt_Prev[0]):,}",styleRight)
        else:
            ResultDate = Paragraph('',styleCenter)
            InvoiceNumber = Paragraph('',styleCenter)
            ProductName = Paragraph('',styleLeft)
            ShippingVolume = Paragraph('',styleRight)      
            Prceeds = Paragraph('',styleRight)

        data = [
                [ResultDate, InvoiceNumber, ProductName, '', ShippingVolume, Prceeds, ''],
        ]

        table = Table(data, colWidths=(18*mm, 18*mm, 61*mm, 20*mm, 21*mm, 25*mm, 30*mm), rowHeights=6.5*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 10),
                ('BOX', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('INNERGRID', (0, 0), (-1, -1), 0.50, colors.dimgray),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        

        if i==0:
            k=0
        else:
            k = i*param
        rowlg = (i+1)*param

        while k < rowlg:
            if k<l:
                row = dt_Detail[k]            

                InvoiceIssueDate = Paragraph(row[0].strftime('%y%m%d'),styleCenter)
                InvoiceNumber = Paragraph(row[1],styleCenter)
                if row[6]>0:
                    #御入金の文言を追加
                    ProductName = Paragraph('御入金(' + row[2] + ')',styleLeft)
                else:
                    ProductName = Paragraph(row[2],styleLeft)
                
                if row[4]=='':
                    ShippingVolume = Paragraph(row[4],styleRight)
                else:
                    ShippingVolume = Paragraph('{:,.2f}'.format(row[4]),styleRight)
                
                Prceeds = Paragraph(f"{int(row[5]):,}",styleRight)
                OrderingCount = Paragraph(row[3],styleRight)
                data += [
                        [InvoiceIssueDate, InvoiceNumber, ProductName, OrderingCount, ShippingVolume, Prceeds, ''],
                ]
            else:
                data += [
                        ['','','','','','',''],
                ]

            table = Table(data, colWidths=(18*mm, 18*mm, 61*mm, 20*mm, 21*mm, 25*mm, 30*mm), rowHeights=6.5*mm)
            table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 10),
                    ('LINEBEFORE', (0, 0), (0, 31), 0.50, colors.dimgray),
                    ('LINEBEFORE', (1, 0), (1, 31), 0.50, colors.dimgray),
                    ('LINEBEFORE', (2, 0), (2, 31), 0.50, colors.dimgray),
                    ('LINEBEFORE', (4, 0), (4, 31), 0.50, colors.dimgray),
                    ('LINEBEFORE', (5, 0), (5, 31), 0.50, colors.dimgray),
                    ('LINEBEFORE', (6, 0), (6, 31), 0.50, colors.dimgray),
                    ('LINEAFTER' , (6, 0), (6, 31), 0.50, colors.dimgray),
                    ('LINEBELOW' , (0, 0), (9, 31), 0.50, colors.dimgray),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
            # 変数加算
            k += 1

        table.wrapOn(pdf_canvas, 10*mm, 10.0*mm)
        table.drawOn(pdf_canvas, 10*mm, 6.5*mm)

        pdf_canvas.showPage()
