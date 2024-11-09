from django.urls import path
#from django.contrib.auth import views as auth_views
from . views import viewscustomer, viewsinit,viewsordering, viewsmerchandise, viewsproductorder, viewsdeposit, viewspayment, viewsrequestresult
from . views import viewsdailyupdate, viewsindividualinvoice, viewsinvoice, viewsCustomerMonthly, viewsSupplierMonthly
from . views import viewsRequestCumulativelist, viewsSalesLedger, viewsPurchaseLedger, viewsunpaid, viewsUnPaidView, viewsUnPaidList
from . views import viewsSalesPersonList, viewshistory, viewsstock, viewscontract
from . output import viewspopdf, viewsProductPdf, viewsindiinvoicepdf, viewsinvoicepdf, viewsCustomerMonthlypdf
from . output import viewsSupplierMonthlypdf, viewsRequestCumulativepdf, viewsSalesLedgerpdf, viewsPurchaseLedgerpdf, viewsUnPaidListpdf
from . output import viewsSalesPersonpdf
# fileupload import
from django.conf import settings
from django.conf.urls.static import static

from django.urls import re_path
from django.views.static import serve  #追加

app_name = "myapp"

urlpatterns = [
    path('', viewsinit.index, name='index'),  
    # signup
    path('signup/', viewsinit.signup, name='signup'),
    ################################################# マスター ###############################################################
    # 得意先仕入先一覧
    path('customersupplier/list/', viewscustomer.CustomerSupplierListView.as_view(), name='list'),
    # 得意先仕入先登録
    path('customersupplier/new/', viewscustomer.CustomerSupplierCreateView.as_view(), name='new'),
    # 得意先仕入先編集
    path('customersupplier/edit/<int:pk>/<int:row>/', viewscustomer.CustomerSupplierUpdateView.as_view(), name='edit'),
    # 得意先仕入先削除
    path('customersupplier/delete/<int:pk>/<int:row>/',viewscustomer.CustomerSupplierDeleteView.as_view(),name='delete'),   
    # 商品マスター一覧
    path('merchandise/list/', viewsmerchandise.MerchandiseListView.as_view(), name='merchandiselist'),
    # 商品マスター登録
    path('merchandise/new/', viewsmerchandise.MerchandiseCreateView.as_view(), name='merchandisenew'),
    # 商品マスター編集
    path('merchandise/edit/<int:pk>/<int:row>/', viewsmerchandise.MerchandiseUpdateView.as_view(), name='merchandiseedit'),
    # 商品マスター削除
    path('merchandise/delete/<int:pk>/<int:row>/',viewsmerchandise.MerchandiseDeleteView.as_view(),name='merchandisedelete'),   
    #################################################  受発注入力 #############################################################
    # 受発注一覧
    path('ordering/list/', viewsordering.OrderingListView.as_view(), name='orderinglist'),
    # 受発注登録
    path('ordering/new/', viewsordering.OrderingCreateView.as_view(), name='orderingnew'),
    # 受発注編集
    path('ordering/edit/<int:pk>/<int:row>/', viewsordering.orderingUpdateView.as_view(), name='orderingedit'),
    # 受発注削除
    path('ordering/delete/<int:pk>/<int:row>/', viewsordering.orderingDeleteView.as_view(), name='orderingdelete'),
    # PDF出力
    path('ordering/pdf/<int:pk>/', viewspopdf.pdf, name='orderingpdf'), 
    #################################################  製品受発注入力 ##########################################################
    # 製品発注一覧
    path('productorder/list/', viewsproductorder.ProductOrderListView.as_view(), name='productorderlist'),
    # 製品発注登録
    path('productorder/new/', viewsproductorder.ProductOrderCreateView.as_view(), name='productordernew'),
    # Ajax処理
    path("productorder/new/exec/", viewsproductorder.ProductOrderCreateView.exec_ajax, name='exec'),
    # 製品発注編集
    path('productorder/edit/<int:pk>/<int:row>/', viewsproductorder.ProductOrderUpdateView.as_view(), name='productorderedit'),
    # 製品発注削除
    path('productorder/delete/<int:pk>/<int:row>/', viewsproductorder.ProductOrderDeleteView.as_view(), name='productorderdelete'),
    # PDF出力
    path('productorder/pdf/<int:pk>/', viewsProductPdf.pdf, name='productorderpdf'),
    ###################################################  実績入力 ############################################################   
    # 受発注実績一覧
    path('requestresult/list/', viewsrequestresult.RequestResultListView.as_view(), name='requestresultlist'),
    # 受発注実績編集
    path('requestresult/edit/<int:pk>/<int:row>/', viewsrequestresult.RequestResultUpdateView.as_view(), name='requestresultedit'),
    # Ajax処理
    path("requestresult/edit/exec_result/", viewsrequestresult.RequestResultUpdateView.exec_ajax_result, name='exec_result'),
    # 本番環境Media参照
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  #追加
    ###################################################  入金支払入力 #########################################################   
    # 入金情報一覧
    path('deposit/list/', viewsdeposit.DepositListView.as_view(), name='Depositlist'),
    # 入金情報登録
    path('deposit/new/', viewsdeposit.DepositCreateView.as_view(), name='Depositnew'),
    # 入金情報編集
    path('deposit/edit/<int:pk>/', viewsdeposit.DepositUpdateView.as_view(), name='Depositedit'),
    # 入金情報削除
    path('deposit/delete/<int:pk>/',viewsdeposit.DepositDeleteView.as_view(),name='Depositdelete'),   

    # 支払情報一覧
    path('payment/list/', viewspayment.PaymentListView.as_view(), name='Paymentlist'),
    # 支払情報登録
    path('payment/new/', viewspayment.PaymentCreateView.as_view(), name='Paymentnew'),
    # 支払情報編集
    path('payment/edit/<int:pk>/', viewspayment.PaymentUpdateView.as_view(), name='Paymentedit'),
    # 支払情報削除
    path('payment/delete/<int:pk>/',viewspayment.PaymentDeleteView.as_view(),name='Paymentdelete'),   
    ###################################################  更新処理 ###########################################################   
    #日次更新対象レコード抽出
    path('dailyupdate/list/', viewsdailyupdate.DailyUpdateListView.as_view(), name='DailyUpdatelist'),
    # 日次更新処理
    path('dailyupdate/update/', viewsdailyupdate.DailyUpdateView.as_view(), name='DailyUpdate'),
    ###################################################  印刷系  ############################################################   
    # 個別請求書一覧
    path('individualinvoice/list/', viewsindividualinvoice.individualinvoiceListView.as_view(), name='individualinvoicelist'),
    # 個別請求書PDF出力
    path('individualinvoice/pdf/<int:pkfrom>/<int:pkto>/<int:isdate>/', viewsindiinvoicepdf.pdf, name='individualinvoicepdf'), 
    # 一括請求一覧
    path('invoice/list/', viewsinvoice.invoiceListView.as_view(), name='invoicelist'),
    # 一括請求書PDF出力
    path('invoice/pdf/<int:pkclosing>/<int:invoiceDate_From>/<int:invoiceDate_To>/<str:element_From>/<str:element_To>/', viewsinvoicepdf.pdf, name='invoicepdf'), 
    # 得意先月次集計
    path('CustomerMonthly/list/', viewsCustomerMonthly.CustomerMonthlyListView.as_view(), name='CustomerMonthlylist'),
    # 得意先月次集計PDF出力
    path('CustomerMonthly/pdf/<int:TargetMonth>/', viewsCustomerMonthlypdf.pdf, name='CustomerMonthlypdf'), 
    # 仕入先月次集計
    path('SupplierMonthly/list/', viewsSupplierMonthly.SupplierMonthlyListView.as_view(), name='SupplierMonthlylist'),
    # 仕入先月次集計PDF出力
    path('SupplierMonthly/pdf/<int:TargetMonth>/', viewsSupplierMonthlypdf.pdf, name='SupplierMonthlypdf'), 
    # 売上台帳
    path('SalesLedger/list/', viewsSalesLedger.SalesLedgerListView.as_view(), name='SalesLedgerlist'),
    # 売上台帳PDF出力
    path('SalesLedger/pdf/<int:TargetMonth>/<str:element_From>/<str:element_To>/', viewsSalesLedgerpdf.pdf, name='SalesLedgerpdf'), 
    # 仕入台帳
    path('PurchaseLedger/list/', viewsPurchaseLedger.PurchaseLedgerListView.as_view(), name='PurchaseLedgerlist'),
    # 仕入台帳PDF出力
    path('PurchaseLedger/pdf/<int:TargetMonth>/<str:element_From>/<str:element_To>/', viewsPurchaseLedgerpdf.pdf, name='PurchaseLedgerpdf'), 
    # 依頼先別累計売上順一覧
    path('requestcumulative/list/', viewsRequestCumulativelist.RequestCumulativeListView.as_view(), name='RequestCumulativelist'),
    # 依頼先別累計売上順一覧PDF出力
    path('requestcumulative/pdf/<int:TargetMonthFrom>/<int:TargetMonthTo>/', viewsRequestCumulativepdf.pdf, name='RequestCumulativepdf'), 
    # 担当者別売上一覧
    path('salesperson/list/', viewsSalesPersonList.SalesPersonListView.as_view(), name='SalesPersonlist'),
    # 担当者別売上一覧PDF出力
    path('salesperson/pdf/<int:TargetMonthFrom>/<int:TargetMonthTo>/<int:TargetUserFrom>/<int:TargetUserTo>/', viewsSalesPersonpdf.pdf, name='SalesPersonpdf'), 
    ###################################################  相殺未払処理 ###########################################################   
    # 未払入力
    path('unpaid/view/', viewsUnPaidView.UnPaidView.as_view(), name='unpaidview'),
    path('unpaid/updatelist/<int:TargetMonth>/', viewsunpaid.UnPaidListView.List, name='unpaidupdatelist'),
    path('unpaid/update', viewsunpaid.UnPaidListView.update, name='unpaidupdate'),
    # 未払一覧表
    path('unpaid/list/', viewsUnPaidList.UnPaidListView.as_view(), name='unpaidlist'),
    path('unpaid/pdf/<int:TargetMonth>/<str:element>/', viewsUnPaidListpdf.pdf, name='UnPaidListpdf'), 
    ###################################################  画面照会 ###########################################################   
    # 履歴一覧
    path('history/list/', viewshistory.HistoryListView.as_view(), name='historylist'),
    # 履歴明細
    path('history/detail/<int:pk>/', viewshistory.HistoryDetailView.as_view(), name='historydetail'),
    # 月末契約残管理
    path('contract/', viewscontract.ContractManageView.as_view(), name='contract'),
    # 契約残抽出
    path('contract/list/<int:TargetMonth>/<int:ManagerCode>', viewscontract.ContractManageView.List, name='contractlist'),
    # Excel出力処理
    path('contract/Excel/<int:TargetMonth>/<int:ManagerCode>', viewscontract.ContractManageView.excel_output, name='excel_output'),

    # 在庫一覧
    path('stock/list/', viewsstock.StockListView.as_view(), name='stocklist'),
    # 在庫明細
    path('stock/detail/<int:pk>/', viewsstock.StockDetailView.as_view(), name='stockdetail'),

] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
                 + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)     
