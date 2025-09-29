from django.http import HttpResponse
from django.shortcuts import render,redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from myapp.output import productorderfunction
# MySQL
import MySQLdb
# 日時
from django.utils import timezone
import datetime
# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def pdf(request,pk):
    try:
        strtime = timezone.now() + datetime.timedelta(hours=9)
        filename = "ProductOrder_" + strtime.strftime('%Y%m%d%H%M%S') + ".pdf"
        response = HttpResponse(status=200, content_type='application/pdf')
        #ダウンロード
        #response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        #Webに表示
        response['Content-Disposition'] = 'filename="{}"'.format(filename)
        make(pk,response)
        UpdateQuery(pk)
    except Exception as e:
        message = "PDF作成時にエラーが発生しました"
        logger.error(message)
        messages.error(request,message) 
        return redirect("myapp:productorderlist")
    return response

def make(pk,response):
    dt = connect(pk)
    dtsize = getsize(pk)
    dtcolor = getcolor(pk)
    dtimage = getimage(pk)
    pdf_canvas = set_info(response) # キャンバス名
    print_string(pdf_canvas,dt,dtsize,dtcolor,dtimage)
    pdf_canvas.save() # 保存

def set_info(response):
    pdf_canvas = canvas.Canvas(response,pagesize=portrait(A4))
    pdf_canvas.setAuthor("hpscript")
    pdf_canvas.setTitle("製品発注書")
    pdf_canvas.setSubject("製品発注書")
    return pdf_canvas

def UpdateQuery(pk):
    conn = MySQLdb.connect(user='root',passwd='PWStools', host='127.0.0.1',db='taudb',port=3308)
    #conn = MySQLdb.connect(user='test',passwd='password', host='127.0.0.1',db='DjangoSample',port=3308)
    cur = conn.cursor()
    sql = (
           ' UPDATE ' 
	           ' myapp_productorder '
	       ' SET ' 	 
		       ' is_Ordered = true '
	       ' WHERE '
		        'id = ' + str(pk) 
        )
    cur.execute(sql)
    result = conn.affected_rows()
    conn.commit()

    cur.close()
    conn.close()

    return result

def connect(pk):
    conn = MySQLdb.connect(user='root',passwd='PWStools', host='127.0.0.1',db='taudb',port=3308)
    #conn = MySQLdb.connect(user='test',passwd='password', host='127.0.0.1',db='DjangoSample',port=3308)
    cur = conn.cursor()
    sql = (
            ' SELECT ' 
            '    CAST(A.id AS CHAR)'
            '   ,J.CustomerName'
            '   ,CASE WHEN A.ProductOrderTitleDiv=1 THEN "様"  WHEN A.ProductOrderTitleDiv=2 THEN "御中" ELSE " " END'
            '   ,A.ProductOrderSlipDiv '
            '   ,A.ProductOrderOrderNumber' 
            '   ,C.McdPartNumber '
            '   ,IFNULL(DATE_FORMAT(A.ProductOrderOrderingDate,"%Y年%m月%d日"),"") '
            '   ,CAST(A.ProductOrderMerchandiseCode_id AS CHAR) '
            '   ,B.CustomerName,IFNULL(DATE_FORMAT(A.ProductOrderDeliveryDate,"%Y年%m月%d日"),"") '
            '   ,A.ProductOrderBrandName '
            '   ,CASE' 
            '       WHEN C.McdUnitPrice % 1 > 0 THEN FORMAT(C.McdUnitPrice,2) '
            '    ELSE '
            '       FORMAT(C.McdUnitPrice,0) '
            '    END '
            '   ,G.McdDtProductName '
            '   ,G.McdDtOrderingCount '
            '   ,G.McdDtStainMixRatio '
            '   ,CASE' 
            '       WHEN G.McdDtlPrice % 1 > 0 THEN FORMAT(G.McdDtlPrice,2) '
            '    ELSE '
            '       FORMAT(G.McdDtlPrice,0) '
            '    END '
            '   ,H.PostCode '
            '   ,H.CustomerName ' 
            '   ,I.prefecturename '
            '   ,H.Municipalities '
            '   ,H.Address '
            '   ,H.BuildingName '
            '   ,H.PhoneNumber '
            '   ,H.FaxNumber '
            '   ,H.EMAIL '
            '   ,A.ProductOrderSupplierPerson '
            '   ,k.first_name '
            '   ,k.last_name '
            '   ,CASE C.McdUnitcode '
            '       WHEN 1 THEN "￥" '
            '                WHEN 2 THEN "US$" '
            '                WHEN 3 THEN "US$" '
            '                WHEN 4 THEN "US$" '
            '                WHEN 5 THEN "US$" '
            '                WHEN 6 THEN "US$" '
            '                WHEN 7 THEN "US$" '
            '       ELSE "" '
            '   END '
            '   ,CASE C.McdUnitcode '
            '       WHEN 1 THEN "" '
            '       WHEN 2 THEN "　FOB東京" '
            '       WHEN 3 THEN "　FOB上海" '
            '       WHEN 4 THEN "　CIF東京" '
            '       WHEN 5 THEN "　CIF上海" '
            '       WHEN 6 THEN "　CMT東京" '
            '       WHEN 7 THEN "　CMT上海" '
            '       ELSE "" '
            '   END '
            '   ,CASE G.McdDtUnitCode '
            '       WHEN 1 THEN "￥" '
            '       WHEN 2 THEN "US$" '
            '       WHEN 3 THEN "US$" '
            '       WHEN 4 THEN "US$" '
            '       WHEN 5 THEN "US$" '
            '       WHEN 6 THEN "US$" '
            '       WHEN 7 THEN "US$" '
            '       ELSE "" '
            '   END '
            '   ,CASE G.McdDtUnitCode '
            '       WHEN 1 THEN "" '
            '       WHEN 2 THEN "FOB東京" '
            '       WHEN 3 THEN "FOB上海" '
            '       WHEN 4 THEN "CIF東京" '
            '       WHEN 5 THEN "CIF上海" '
            '       WHEN 6 THEN "CMT東京" '
            '       WHEN 7 THEN "CMT上海" '
            '       ELSE "" '
            '   END '
            '   ,L.CustomerName '
            '   ,A.ProductOrderMarkName '
            '   ,A.ProductOrderSummary '
            '   ,C.McdTempPartNumber '
            ' FROM '
            '   myapp_productorder A '
            '   LEFT JOIN ' 
            '   auth_user k on '
            '       A.ManagerCode = k.id'
            '   LEFT JOIN '
            '   myapp_customersupplier B on '
            '       A.ProductOrderApparelCode_id = b.id '
            '   LEFT JOIN '
            '   myapp_merchandise C on '
            '       A.ProductOrderMerchandiseCode_id = C.id '
            '   LEFT JOIN '
            '  	myapp_customersupplier J on	'
            '      A.ProductOrderDestinationCode_id = J.id '
            '   LEFT JOIN '
            '   myapp_merchandisedetail G on '
            '       C.id = G.McdDtid_id '
            '   AND G.is_Deleted = 0 '
            '   LEFT JOIN '
            '  	myapp_customersupplier L on	'
            '      A.ProductOrderSupplierCode_id = L.id '
            '   ,(SELECT PostCode,CustomerName,PrefecturesCode_id,Municipalities,Address,BuildingName,PhoneNumber,FaxNumber,EMAIL FROM myapp_customersupplier WHERE CustomerCode = "A0042" AND is_Deleted = 0) H '
            '   LEFT JOIN '
            '   myapp_prefecture I on '
            '       H.PrefecturesCode_id = I.id '
            ' WHERE '
            '       A.id = ' + str(pk) +
            ' ORDER BY '
            '   G.id '
            )
    cur.execute(sql)
    result = cur.fetchall()     

    cur.close()
    conn.close()

    return result

def getsize(pk):
    conn = MySQLdb.connect(user='root',passwd='PWStools', host='127.0.0.1',db='taudb',port=3308)
    #conn = MySQLdb.connect(user='test',passwd='password', host='127.0.0.1',db='DjangoSample',port=3308)
    cur = conn.cursor()
    sql = (
                ' SELECT '
                ' 	 substr(B.McdSize,1,7) '
                ' FROM '
                '	myapp_productorder A '
                '	LEFT JOIN '
                '	myapp_merchandisesize B on '
                '		A.ProductOrderMerchandiseCode_id = B.McdSizeId_id '
                ' WHERE '
                '     A.id = ' + str(pk) +
                ' AND B.is_Deleted = 0 '
            )
    cur.execute(sql)
    result = cur.fetchall()     

    cur.close()
    conn.close()

    return result

def getcolor(pk):
    conn = MySQLdb.connect(user='root',passwd='PWStools', host='127.0.0.1',db='taudb',port=3308)
    #conn = MySQLdb.connect(user='test',passwd='password', host='127.0.0.1',db='DjangoSample',port=3308)
    cur = conn.cursor()
    sql = (
            ' select '
            '	  color '
            '    ,group_concat(size order by id,size) key_list ' 
            '    ,group_concat(max_value order by id,size) value_list '
            '    ,colorNumber '
            ' from '
            ' ( '
            '  SELECT '
            '	 a.id			                                                        AS id '
            #'	,concat(substr(b.McdColorNumber,1,8)," ",substr(b.McdColor,1,8))        AS color '
            # カラーのみ
            '	,substr(b.McdColor,1,20)                                                AS color '
            '	,substr(c.McdSize,1,7)			                                        AS size ' 
            '	,max(a.PodVolume) 	                                                    AS max_value '
            '  	,substr(b.McdColorNumber,1,6)                                           AS colorNumber '
            '  FROM '
            '	myapp_productorderdetail a '
            '	left join '
            '	myapp_merchandisecolor b on '
            '		a.PodColorId_id = b.id '
            '	left join '
            '	myapp_merchandisesize c on '
            '		a.PodsizeId_id = c.id '
            ' WHERE '
            '	  a.PodDetailId_id = ' + str(pk) +
            ' AND b.is_Deleted = 0 '
            ' AND c.is_Deleted = 0 '
            '  GROUP BY ' 
            '	b.McdColor, c.McdSize, b.McdColorNumber'
            ' ) t '
            ' group by' 
            '	 color '
            '   ,colorNumber'
            ' order by'
            '    t.id '
            )
    cur.execute(sql)
    result = cur.fetchall()     

    cur.close()
    conn.close()

    return result

def getimage(pk):
    conn = MySQLdb.connect(user='root',passwd='PWStools', host='127.0.0.1',db='taudb',port=3308)
    #conn = MySQLdb.connect(user='test',passwd='password', host='127.0.0.1',db='DjangoSample',port=3308)
    cur = conn.cursor()
    sql = (
            ' SELECT ' 
            '    A.id ' 
            '	,IFNULL(C.uploadPath,"") ' 
            ' FROM ' 
            '	myapp_productorder A '
            '   LEFT JOIN '
            '   myapp_merchandise B ON '
            '       A.ProductOrderMerchandiseCode_id = B.id '
			'	LEFT JOIN ' 
          	'	myapp_merchandisefileupload C ON '
            '		B.id = C.McdDtuploadid_id '
            ' WHERE '
            '     A.id = ' + str(pk) +
            ' AND B.is_Deleted = 0 '
            ' AND C.is_Deleted = 0 ' 
            )
    cur.execute(sql)
    result = cur.fetchall()     

    cur.close()
    conn.close()

    return result

#製品発注書発行
def print_string(pdf_canvas,dt,dtsize,dtcolor,dtimage):
    productorderfunction.printstring(pdf_canvas,dt,dtsize,dtcolor,dtimage)
     
if __name__ == '__main__':
    make()
