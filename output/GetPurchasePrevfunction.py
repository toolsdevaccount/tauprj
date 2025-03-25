from myapp.models import Payment, RequestResult
# 検索機能のために追加
from django.db.models import Q
# 計算用
from django.db.models import Sum,F,IntegerField
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth

#前月までの支払合計額を取得
def GetPayPrvSum(search_date, Customer):
    queryset = Payment.objects.filter(
        PaymentDate__lte=(str(search_date[3])),
        PaymentSupplierCode=(str(Customer[0]['id'])),
        is_Deleted=0
        )
    
    queryset = queryset.filter(~Q(PaymentDiv=11))

    PayPrvSum = list(
        queryset.values(
            'PaymentSupplierCode'
            ).annotate(
                Pay_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
                ))

    return PayPrvSum

#前月までの課税仕入合計額を取得
def GetStockPrvSum(search_date, Customer):
    StockPrvSum =  RequestResult.objects.annotate(
        monthly=TruncMonth('InvoiceIssueDate')
        ).values(
            'monthly',
            'id',
        ).filter(
            InvoiceIssueDate__lte=(str(search_date[3])),
            OrderingId__SupplierCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            OrderingDetailId_id__is_Taxation=1,
            ResultMoveDiv=0,
            ).annotate(
                    Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()),
                ).order_by(
                    'monthly'
                )

    return StockPrvSum

#前月までの非課税仕入合計額を取得
def GetPrvTaxExempt(search_date, Customer):
    PrvTaxExempt =  RequestResult.objects.annotate(
        monthly=TruncMonth('InvoiceIssueDate')
        ).values(
            'monthly'
        ).filter(
            InvoiceIssueDate__lte=(str(search_date[3])),
            OrderingId__SupplierCode=(str(Customer[0]['id'])),
            InvoiceNUmber__gt=0,
            InvoiceIssueDiv=1,
            is_Deleted=0,
            OrderingDetailId_id__is_Taxation=0,
            ResultMoveDiv=0,
            ).annotate(
                    Abs_total=Sum(Coalesce(F('ShippingVolume'),0) * Coalesce(F('OrderingDetailId__DetailUnitPrice'),0),output_field=IntegerField()),
                )
    return PrvTaxExempt

#前月までの消費税調整額を取得
def GetPrevAdjustment(search_date, Customer):
    Adjustment = Payment.objects.values(
        'PaymentSupplierCode'
        ).annotate(
            Adjustment_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
            ).filter(
                 PaymentDate__lte=(str(search_date[3]))
                ,PaymentSupplierCode=(str(Customer[0]['id']))
                ,is_Deleted=0
                ,PaymentDiv=11
                )

    return Adjustment

#前月までの消費税調整額レコードを取得
def GetPrevAdjustmentDetail(search_date, Customer):
    #消費税調整抽出
    PrvAdjustment = Payment.objects.values(
        'PaymentSupplierCode',
        'id',
        ).annotate(
            Adjustment_total=Coalesce(Sum('PaymentMoney'),0,output_field=IntegerField())
            ).filter(
                PaymentDate__lte=(str(search_date[3])),
                PaymentSupplierCode=(str(Customer[0]['id'])),
                is_Deleted=0,
                PaymentDiv=11,
                ).order_by(
                    'PaymentDate'
                )

    PrvAdjustment = list(PrvAdjustment.values('Adjustment_total'))

    return PrvAdjustment
