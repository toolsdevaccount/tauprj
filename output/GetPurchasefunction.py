from myapp.models import Payment, RequestResult
# 検索機能のために追加
from django.db.models import Q, Max
# 計算用
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce

#当月支払額を取得
def GetPaySum(search_date, Customer):
    queryset = Payment.objects.filter(
        PaymentDate__range=(str(search_date[0]),str(search_date[1])),
        PaymentSupplierCode=(str(Customer[0]['id'])),
        is_Deleted=0
        )
    queryset = queryset.filter(~Q(PaymentDiv=11))
    PaySum = list(queryset.values(
        'PaymentSupplierCode'
        ).annotate(
            Pay_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
            ))

    return PaySum

#当月支払消費税調整額を取得
def GetAdjustment(search_date, Customer):
    Adjustment = Payment.objects.values('PaymentSupplierCode').annotate(
                                        Adjustment_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
                                        ).filter(
                                             PaymentDate__range=(str(search_date[0]),str(search_date[1]))
                                            ,PaymentSupplierCode=(str(Customer[0]['id']))
                                            ,is_Deleted=0
                                            ,PaymentDiv=11
                                            )
    Adjustment = list(Adjustment.values('Adjustment_total'))

    return Adjustment

#当月課税分仕入集計を取得
def GetPurchaseTaxRow(search_date, Customer):
    queryset =  RequestResult.objects.values(
        'ShippingVolume',
        'OrderingDetailId__DetailUnitPrice'
        ).filter(
            InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
            OrderingId__SupplierCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            OrderingDetailId_id__is_Taxation=1,
            ResultMoveDiv=0,
            )
    return queryset

#当月非課税分仕入集計を取得
def GetPurchaseRow(search_date, Customer):
    queryset =  RequestResult.objects.values(
        'ShippingVolume',
        'OrderingDetailId__DetailUnitPrice'
        ).filter(
            InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
            OrderingId__SupplierCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            OrderingDetailId_id__is_Taxation=0,
            ResultMoveDiv=0,
            )
    return queryset
#当月仕入合計額を取得
def GetStockSum(search_date, Customer):
    queryset =  RequestResult.objects.filter(InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
                OrderingId__SupplierCode=(str(Customer[0]['id'])),
                InvoiceNUmber__gt=0,
                InvoiceIssueDiv=1,
                is_Deleted=0,
                )

    StockSum =  list(queryset.values(
        'OrderingId__SupplierCode',
        'id',
        'InvoiceNUmber'
        ).annotate(
            Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()))
            )

    return StockSum

#当月課税分仕入レコードを取得
def GetPurchaseTaxDetail(search_date, Customer):
    queryset =  RequestResult.objects.filter(
        InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
        OrderingId__SupplierCode=(str(Customer[0]['id'])),
        InvoiceNUmber__gt=0,
        InvoiceIssueDiv=1,
        is_Deleted=0,
        OrderingDetailId__DetailUnitPrice__gt=0,
        OrderingDetailId_id__is_Taxation=1,
        )
    queryset =  queryset.values(
        'SlipNumber',
        'OrderingId__SupplierCode', 
        'OrderingDetailId__DetailUnitPrice',
        'id',
        ).annotate(
            Abs_total=Sum(F('ShippingVolume') * F('OrderingDetailId__DetailUnitPrice')),
            Shipping_total=Sum('ShippingVolume'),
            ResultDate_Max=Max('ResultDate'),
            ProductName_Max=Max('OrderingId__ProductName'),
            OrderingCount_Max=Max('OrderingId__OrderingCount'),
            SlipDiv_Max=Max('OrderingId__SlipDiv'),
            OrderNumber_Max=Max('OrderingId__OrderNumber'),
            SlipNumber_Max=Max('SlipNumber'),
            ShippingVolume_Max=Max('ShippingVolume'),
            DetailUnitPrice_Max=Max('OrderingDetailId__DetailUnitPrice'),
            ShippingDate_Max=Max('ShippingDate'),
            InvoiceIssueDate_Max=Max('InvoiceIssueDate'),
            ).order_by(
                'InvoiceIssueDate',
                'ShippingDate',
                'SlipNumber'
                )
    return queryset
#当月非課税分仕入レコードを取得
def GetPurchaseDetail(search_date, Customer):
    queryset =  RequestResult.objects.filter(
        InvoiceIssueDate__range=(str(search_date[0]),str(search_date[1])),
        OrderingId__SupplierCode=(str(Customer[0]['id'])),
        InvoiceNUmber__gt=0,
        InvoiceIssueDiv=1,
        is_Deleted=0,
        OrderingDetailId__DetailUnitPrice__gt=0,
        OrderingDetailId_id__is_Taxation=0,
        )
    queryset =  queryset.values(
        'SlipNumber',
        'OrderingId__SupplierCode', 
        'OrderingDetailId__DetailUnitPrice',
        'id',
        ).annotate(
            Abs_total=Sum(F('ShippingVolume') * F('OrderingDetailId__DetailUnitPrice')),
            Shipping_total=Sum('ShippingVolume'),
            ResultDate_Max=Max('ResultDate'),
            ProductName_Max=Max('OrderingId__ProductName'),
            OrderingCount_Max=Max('OrderingId__OrderingCount'),
            SlipDiv_Max=Max('OrderingId__SlipDiv'),
            OrderNumber_Max=Max('OrderingId__OrderNumber'),
            SlipNumber_Max=Max('SlipNumber'),
            ShippingVolume_Max=Max('ShippingVolume'),
            DetailUnitPrice_Max=Max('OrderingDetailId__DetailUnitPrice'),
            ShippingDate_Max=Max('ShippingDate'),
            InvoiceIssueDate_Max=Max('InvoiceIssueDate'),
            ).order_by(
                'InvoiceIssueDate',
                'ShippingDate',
                'SlipNumber'
                )
    return queryset
#当月支払レコードを取得
def GetPayDetail(search_date, Customer):
    queryset_pay = Payment.objects.filter(
        PaymentDate__range=(str(search_date[0]),str(search_date[1])),
        PaymentSupplierCode=(str(Customer[0]['id'])),
        is_Deleted=0
        )
    queryset_pay = queryset_pay.filter(~Q(PaymentDiv=11))
    queryset_pay =  queryset_pay.values(
        'PaymentDate',
        'PaymentDiv__DepoPayDivname',
        'PaymentSummary',
        'PaymentMoney'
        )
    return queryset_pay
#当月支払消費税調整レコードを取得
def GetAdjustmentDetail(search_date, Customer):
    queryset_adjust = Payment.objects.filter(
        PaymentDate__range=(str(search_date[0]),str(search_date[1])),
        PaymentSupplierCode=(str(Customer[0]['id'])),
        is_Deleted=0
        )
    queryset_adjust = queryset_adjust.filter(PaymentDiv=11)
    queryset_adjust =  queryset_adjust.values(
        'PaymentDate',
        'PaymentDiv__DepoPayDivname',
        'PaymentSummary',
        'PaymentMoney'
        )
    return queryset_adjust
