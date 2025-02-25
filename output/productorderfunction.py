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
# 文字列折り返し
import textwrap
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def printstring(pdf_canvas,dt,dtsize,dtcolor,dtimage):
    # フォント登録
    YuGosic = "YuGothR.ttc"
    YuGosicB = "YuGothB.ttc"
    pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))

    # 線の色
    pdf_canvas.setStrokeColor(dimgrey)
    # 線の太さ
    pdf_canvas.setLineWidth(0.25)

    # 発注先
    font_size = 14
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(43, 760, dt[0][1] + '　' + dt[0][25] + dt[0][2])

    # 発注日
    font_size = 11
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(480, 790, dt[0][6])

    # 発注番号
    font_size = 10
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(480, 780, 'No　' + dt[0][0])

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
    pdf_canvas.drawImage(img, 165*mm, 258*mm , 45.0*mm, 12.0*mm)

    pdfmetrics.registerFont(TTFont('游ゴシック 標準', YuGosic))

    font_size = 10
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(357, 720, '〒 ' + dt[0][16])
    pdf_canvas.drawString(357, 710, dt[0][18] + dt[0][19] + dt[0][20] + dt[0][21])
    pdf_canvas.drawString(385, 700, 'TEL: ' + dt[0][22] + ' FAX: ' + dt[0][23])

    # title
    font_size = 16
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(250, 810, '製 品 発 注 書')

    # メッセージ
    font_size = 10
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(130, 670,'下記の通り発注いたしますので、御手配のほどよろしくお願い申し上げます')

    # オーダーNO
    pdf_canvas.setFillColor(colors.HexColor("#87CAD7"))    # 塗りつぶしの色を設定
    pdf_canvas.rect(34, 600, 76, 60, fill=True)            # 四角形を描画

    pdf_canvas.line(110, 660, 110, 600) #中縦
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(40, 645,'オーダーNO')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(120,645, dt[0][3] + '-' + dt[0][4])
    pdf_canvas.rect(110, 640, 70, 20)               # 四角形を描画
    pdf_canvas.line(34, 640, 110, 640)              # オーダーNOの下

    # アパレル
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(40, 625,'アパレル')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(120,625, dt[0][8])

    # ブランド名
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(40, 605,'ブランド')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(120,605, dt[0][10])
    pdf_canvas.setFillColor(colors.HexColor("#87CAD7"))         # 塗りつぶしの色を設定
    pdf_canvas.rect(180, 640, 70, 20, fill=True)                # 四角形を描画

    # 本品番
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(200, 645,'本品番')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(260,645, dt[0][5])
    pdf_canvas.rect(250, 640, 120, 20)                          # 四角形を描画


    # 商品コード
    pdf_canvas.setFillColor(colors.HexColor("#87CAD7"))         # 塗りつぶしの色を設定
    pdf_canvas.rect(370, 600, 70, 60, fill=True)                # 四角形を描画
    pdf_canvas.setFillColor(colors.white) 
    font_size = 9
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(380, 645,'商品コード')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(450, 645, dt[0][7])
    pdf_canvas.rect(440, 600, 125, 60)                          # 四角形を描画
    pdf_canvas.line(370, 640, 565, 640)                         # 商品コードの下

    # 線の太さ
    pdf_canvas.setLineWidth(0.1)
    pdf_canvas.line(34, 620, 565, 620)                          # アパレル - 納期の下
    pdf_canvas.line(110, 600, 440, 600)                         # ブランド下

    # 納期
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(380, 625,'納　期')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(450, 625, dt[0][9])

    # 仕入単価
    font_size = 9
    pdf_canvas.setFillColor(colors.white) 
    pdf_canvas.setFont('游ゴシック 太字', font_size)
    pdf_canvas.drawString(380, 605,'仕入単価')
    pdf_canvas.setFillColor(colors.black) 
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(450, 605, dt[0][28] + dt[0][11] + dt[0][29])

    # 品名、番手、混率、単価、条件
    style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=9, textColor='white', alignment=TA_CENTER)
    itemNo0 = Paragraph('品' + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '名',style)
    itemNo1 = Paragraph('番' + '&nbsp;&nbsp;&nbsp;&nbsp;' + '手',style)
    itemNo2 = Paragraph('混' + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + '率',style)
    itemNo3 = Paragraph('単' + '&nbsp;&nbsp;&nbsp;&nbsp;' + '価',style)
    itemNo4 = Paragraph('条' + '&nbsp;&nbsp;&nbsp;&nbsp;' + '件',style)

    data = [
        [itemNo0, itemNo1, itemNo2, itemNo3, itemNo4] ,
    ]

    table = Table(data, colWidths=(45*mm, 22*mm, 70*mm, 30*mm, 20*mm), rowHeights=7.0*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 9),
            ('BACKGROUND', (0, 0), (4, 0), colors.HexColor("#87CAD7")),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 15*mm, 10*mm)
    table.drawOn(pdf_canvas, 12*mm, 201.0*mm)

    data =[]
    l=len(dt)
    styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_LEFT)
    styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)
    styleCenter = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_CENTER)

    for i in range(7):
        if i<l: 
            row = dt[i]
            # 指定した列の左寄せ
            ProductName = Paragraph(row[12],styleLeft)
            OrderingCount = Paragraph(row[13],styleCenter)
            StainMixRatio = Paragraph(row[14],styleLeft)
            UnitDiv = Paragraph(row[31],styleLeft)
            # 指定した列の右寄せ
            if row[15]=='0':   #0を空白に変換する
                DtlPrice = Paragraph(f" ",styleRight)
            else:
                DtlPrice = Paragraph(row[30] + row[15],styleRight)

            data += [
                    [ProductName, OrderingCount, StainMixRatio, DtlPrice, UnitDiv],
            ]
        else:
            data += [
                    ['','','','',''],
            ]

        table = Table(data, colWidths=(45*mm, 22*mm, 70*mm, 30*mm, 20*mm), rowHeights=7.0*mm)
        table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 9),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgrey),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.dimgrey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))

    table.wrapOn(pdf_canvas, 15*mm, 10*mm)
    table.drawOn(pdf_canvas, 12*mm, 152.0*mm)

    # サイズ
    data =[]
    l=len(dtsize)

    style = ParagraphStyle(name='Normal', fontName='游ゴシック 太字', fontSize=9, textColor='white', alignment=TA_CENTER)
    titleNo0 = Paragraph('カラー/サイズ',style)
    titleNo8 = Paragraph('合' + '&nbsp' + '計',style)

    for i in range(6):
        if i<l: 
            row = dtsize[i]
            if i==0:
                titleNo2 = Paragraph(row[0],style)
            if i==1:
                titleNo3 = Paragraph(row[0],style)
            if i==2:
                titleNo4 = Paragraph(row[0],style)
            if i==3:
                titleNo5 = Paragraph(row[0],style)
            if i==4:
                titleNo6 = Paragraph(row[0],style)
            if i==5:
                titleNo7 = Paragraph(row[0],style)
        else:
            if i==0:
                titleNo2 = ''
            if i==1:
                titleNo3 = ''
            if i==2:
                titleNo4 = ''
            if i==3:
                titleNo5 = ''
            if i==4:
                titleNo6 = ''
            if i==5:
                titleNo7 = ''

    data = [
        [titleNo0, titleNo2, titleNo3, titleNo4, titleNo5, titleNo6, titleNo7, titleNo8] ,
    ]

    table = Table(data, colWidths=(39*mm, 21*mm, 21*mm, 21*mm, 21*mm, 21*mm, 21*mm, 22*mm), rowHeights=7.0*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), '游ゴシック 太字', 9),
            ('BACKGROUND', (0, 0), (7, 0), colors.HexColor("#87CAD7")),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgrey),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.dimgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    table.wrapOn(pdf_canvas, 15*mm, 10*mm)
    table.drawOn(pdf_canvas, 12*mm, 141*mm)

    # カラー
    data =[]
    l=len(dtcolor)
    total = 0
    itemNo12total = 0
    itemNo13total = 0
    itemNo14total = 0
    itemNo15total = 0
    itemNo16total = 0
    itemNo17total = 0

    style = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_CENTER)
    #フォントサイズ8
    style8 = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=8, alignment=TA_LEFT)
    styleLeft = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_LEFT)
    styleRight = ParagraphStyle(name='Normal', fontName='游ゴシック 標準', fontSize=9, alignment=TA_RIGHT)

    for i in range(9):
        if i<l:
            row = dtcolor[i]
            itemNo11 = Paragraph(row[0],style8)
            item = row[2]
            Vol = item.split(',')
            col = len(Vol)
            itemNo12 = ""
            itemNo13 = ""
            itemNo14 = ""
            itemNo15 = ""
            itemNo16 = ""
            itemNo13 = ""
            itemNo14 = ""
            itemNo15 = ""
            itemNo16 = ""
            itemNo17 = ""
            total = 0
            for k in range(col):
                if k==0:
                    if Vol[0]=='0':   #0を空白に変換する
                        itemNo12 = Paragraph(f" ",styleRight)
                    else:
                        itemNo12 = Paragraph(f"{int(Decimal(Vol[0])):,}",styleRight)

                    total += int(Decimal(Vol[0]))
                    itemNo12total += int(Decimal(Vol[0]))
                if k==1:
                    if Vol[1]=='0':   #0を空白に変換する
                        itemNo13 = Paragraph(f" ",styleRight)
                    else:
                        itemNo13 = Paragraph(f"{int(Decimal(Vol[1])):,}",styleRight)
                    total += int(Decimal(Vol[1]))
                    itemNo13total += int(Decimal(Vol[1]))
                if k==2:
                    if Vol[2]=='0':   #0を空白に変換する   
                        itemNo14 = Paragraph(f" ",styleRight)
                    else:
                        itemNo14 = Paragraph(f"{int(Decimal(Vol[2])):,}",styleRight)
                    total += int(Decimal(Vol[2]))
                    itemNo14total += int(Decimal(Vol[2]))
                if k==3:
                    if Vol[3]=='0':   #0を空白に変換する
                        itemNo15 = Paragraph(f" ",styleRight)
                    else:
                        itemNo15 = Paragraph(f"{int(Decimal(Vol[3])):,}",styleRight)
                    total += int(Decimal(Vol[3]))
                    itemNo15total += int(Decimal(Vol[3]))
                if k==4:
                    if Vol[4]=='0':   #0を空白に変換する   
                        itemNo16 = Paragraph(f" ",styleRight)
                    else:
                        itemNo16 = Paragraph(f"{int(Decimal(Vol[4])):,}",styleRight)
                    total += int(Decimal(Vol[4]))
                    itemNo16total += int(Decimal(Vol[4]))
                if k==5:   
                    if Vol[5]=='0':   #0を空白に変換する   
                        itemNo17 = Paragraph(f" ",styleRight)
                    else:
                        itemNo17 = Paragraph(f"{int(Decimal(Vol[5])):,}",styleRight)
                    total += int(Decimal(Vol[5]))
                    itemNo17total += int(Decimal(Vol[5]))
            detailtotal = Paragraph(f"{int(Decimal(total)):,}",styleRight)
            data += [
                [itemNo11,itemNo12,itemNo13,itemNo14,itemNo15,itemNo16,itemNo17,detailtotal] ,
            ]
        else:
            if i==8:
                # 総合計の計算
                itemtotal = Decimal(itemNo12total) + Decimal(itemNo13total) + Decimal(itemNo14total) + Decimal(itemNo15total) + Decimal(itemNo16total) + Decimal(itemNo17total)
                itemtotal = Paragraph(f"{Decimal(itemtotal):,}",styleRight)
                # 指定した列の右寄せ
                if Decimal(itemNo12total) != 0:
                    itemNo12total = Paragraph(f"{Decimal(itemNo12total):,}",styleRight)
                else:
                    itemNo12total = ''

                if Decimal(itemNo13total) != 0:
                    itemNo13total = Paragraph(f"{Decimal(itemNo13total):,}",styleRight)
                else:
                    itemNo13total = ''

                if Decimal(itemNo14total) != 0:
                    itemNo14total = Paragraph(f"{Decimal(itemNo14total):,}",styleRight)
                else:
                    itemNo14total = ''

                if Decimal(itemNo15total) != 0:
                    itemNo15total = Paragraph(f"{Decimal(itemNo15total):,}",styleRight)
                else:
                    itemNo15total = ''

                if Decimal(itemNo16total) != 0:
                    itemNo16total = Paragraph(f"{Decimal(itemNo16total):,}",styleRight)
                else:
                    itemNo16total = ''

                if Decimal(itemNo17total) != 0:
                    itemNo17total = Paragraph(f"{Decimal(itemNo17total):,}",styleRight)
                else:
                    itemNo17total = ''

                data += [
                    [Paragraph('合&nbsp計',style),itemNo12total,itemNo13total,itemNo14total,itemNo15total,itemNo16total,itemNo17total ,itemtotal] ,
                ]
            else:
                data += [
                    ['','','','','','','',''] ,
                ]

    table = Table(data, colWidths=(39*mm, 21*mm, 21*mm, 21*mm, 21*mm, 21*mm, 21*mm, 22*mm), rowHeights=7.0*mm)
    table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), '游ゴシック 標準', 9),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.dimgrey),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.dimgrey),
            ('LINEABOVE', (0, 1), (0, 8), 0.25, colors.dimgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
    table.wrapOn(pdf_canvas, 15*mm, 10*mm)
    table.drawOn(pdf_canvas, 12*mm, 78*mm)

    # 文字列
    font_size = 9
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(40, 208,'備　考')

    # 画像ファイル数算出
    l=len(dtimage)

    # イメージ(画像ファイルを挿入)
    for i in range(l):
        row = dtimage[i]
        if row[1]!="":
            #img = './mysite/media/' + row[1]
            img = './media/' + row[1]

            if i==0:
                pdf_canvas.drawImage(img, 16*mm, 25*mm , 30.0*mm, 30.0*mm, preserveAspectRatio=True)
            if i==1:
                pdf_canvas.drawImage(img, 60*mm, 25*mm , 30.0*mm, 30.0*mm, preserveAspectRatio=True)

    #if l > 0:
    # 仮品番
    font_size = 9
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(40, 190,'仮品番')
    pdf_canvas.drawString(100 ,190, dt[0][35])

    # 備考
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    text = textwrap.wrap(dt[0][34], 20)
    x = 190
    for contents in text:
        contents.encode('utf-8')
        pdf_canvas.drawString(250, x, contents)
        x=x-10
    # 
    font_size = 14
    pdf_canvas.setFont('游ゴシック 標準', font_size)
    pdf_canvas.drawString(350, 75,'Signature')
    pdf_canvas.line(350, 70, 520, 70) 

    #備考BOX
    pdf_canvas.rect(33, 57, 533, 147) 

    pdf_canvas.showPage()
