from myapp.models import RequestResult, Inventory
# 検索機能のために追加
from django.db.models import Q, Max, Sum, F

#在庫一覧
def GetCarryFowardRecord(OrderInput):
    CarryForward_Record = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ProductName=Max('OrderingId__ProductName'),
            OrderingCount=Max('OrderingId__OrderingCount'),
            DestinationCustomerCode=Max('OrderingId__DestinationCode_id__CustomerCode'),
            DestinationCustomer=Max('OrderingId__DestinationCode_id__CustomerOmitName'),
            RequestCustomerCode=Max('OrderingId__RequestCode_id__CustomerCode'),
            RequestCustomer=Max('OrderingId__RequestCode_id__CustomerOmitName'),       
            ShippingCustomerCode=Max('OrderingId__ShippingCode_id__CustomerCode'),
            ShippingCustomer=Max('OrderingId__ShippingCode_id__CustomerOmitName'),
            DetailUnitPrice=Max('OrderingDetailId__DetailUnitPrice'),
            ProcessingUnitprice=Max(0),
            StockSummary=Max(0),
            CarryForward_total=Max(0),
            ReciveStock=Max(0),
            Issue=Max(0),
            Remaining=Max(0),
            Process_total=Max(0),
            Process=Max(0),
            Balance=Max(0),
            Manager_firstname=Max('OrderingId__RequestCode_id__ManagerCode__first_name'),
            Manager_lastname=Max('OrderingId__RequestCode_id__ManagerCode__last_name'),
            DetailColor=Max('OrderingDetailId__DetailColor'),
            InventoryVol_total=Max(0),
            InventoryPrice_total=Max(0),
            ManufacturingVol_total=Max(0),
            ManufacturingPrice_total=Max(0)
        ).filter(
            Q(OrderingId__SlipDiv='S') | 
            Q(OrderingId__SlipDiv='T') | 
            Q(OrderingId__SlipDiv='M') | 
            Q(OrderingId__SlipDiv='N') | 
            Q(OrderingId__SlipDiv='W') |
            Q(OrderingId__SlipDiv='P') | 
            Q(OrderingId__SlipDiv='I') | 
            Q(OrderingId__SlipDiv='E') | 
            Q(OrderingId__SlipDiv='D') | 
            Q(OrderingId__SlipDiv='B') ,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_Record

#加工在庫一覧
def GetCarryForwardProcess(OrderInput):
    CarryForward_Process = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ProductName=Max('OrderingId__ProductName'),
            OrderingCount=Max('OrderingId__OrderingCount'),
            DestinationCustomerCode=Max('OrderingId__DestinationCode_id__CustomerCode'),
            DestinationCustomer=Max('OrderingId__DestinationCode_id__CustomerOmitName'),
            RequestCustomerCode=Max('OrderingId__RequestCode_id__CustomerCode'),
            RequestCustomer=Max('OrderingId__RequestCode_id__CustomerOmitName'),
            ShippingCustomerCode=Max('OrderingId__ShippingCode_id__CustomerCode'),
            ShippingCustomer=Max('OrderingId__ShippingCode_id__CustomerOmitName'),
            DetailUnitPrice=Max(0),
            ProcessingUnitprice=Max('OrderingDetailId__DetailUnitPrice'),
            StockSummary=Sum('ShippingVolume'),
            CarryForward_total=Max(0),
            ReciveStock=Max(0),
            Issue=Max(0),
            Remaining=Max(0),
            Process_total=Max(0),
            Process=Max(0),
            Balance=Max(0),
            Manager_firstname=Max('OrderingId__RequestCode_id__ManagerCode__first_name'),
            Manager_lastname=Max('OrderingId__RequestCode_id__ManagerCode__last_name'),
            DetailColor=Max('OrderingDetailId__DetailColor'),
            InventoryVol_total=Max(0),
            InventoryPrice_total=Max(0),
            ManufacturingVol_total=Max(0),
            ManufacturingPrice_total=Max(0)
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='C') | 
            Q(OrderingId__SlipDiv='X'),
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )
    
    return CarryForward_Process

#繰越入庫
def GetCarryForwardReciveStock(search_date,OrderInput):
    CarryForward_ReciveStock = RequestResult.objects.values(
        'id',
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ReciveStock_total=Sum('ShippingVolume'),
            DetailUnitPrice=F('OrderingDetailId__DetailUnitPrice'),
        ).filter(
            Q(OrderingId__SlipDiv='S') | 
            Q(OrderingId__SlipDiv='T') | 
            Q(OrderingId__SlipDiv='M') | 
            Q(OrderingId__SlipDiv='N') | 
            Q(OrderingId__SlipDiv='W') ,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(search_date[0]),
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_ReciveStock

#繰越出庫
def GetCarryForwardIssue(search_date,OrderInput):
    CarryForward_Issue = RequestResult.objects.values(
        'id',
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            Issue_total=Sum('ShippingVolume'),
        ).filter(
            Q(OrderingId__SlipDiv='P') | 
            Q(OrderingId__SlipDiv='I') | 
            Q(OrderingId__SlipDiv='E') | 
            Q(OrderingId__SlipDiv='D') | 
            Q(OrderingId__SlipDiv='B') ,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(search_date[0]),
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_Issue

#繰越加工
def GetCarryForwardProcessStock(search_date,OrderInput):
    CarryForward_ProcessStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ProcessStock_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            OrderingId__OrderNumber__in=OrderInput,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(search_date[0]),
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_ProcessStock

#調整残高
def GetCarryForwardInventory(OrderInput):
    CarryForward_Inventory = Inventory.objects.values(
        'OrderNumber',
        'ResultItemNumber',
        ).annotate(
            InventoryVol_total=Sum('InventoryVol'),
            InventoryPrice_total=Sum('InventoryPrice'),
            ManufacturingVol_total=Sum('ManufacturingVol'),
            ManufacturingPrice_total=Sum('ManufacturingPrice'),
        ).filter(
            is_Deleted=0, 
            OrderNumber__in=OrderInput,
            ).order_by(
                'OrderNumber'
                )

    return CarryForward_Inventory
#入庫
def GetReciveStock(search_date,OrderInput):
    ReciveStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'id',
        'ResultItemNumber',
        ).annotate(
            Recive_total=Sum('ShippingVolume'),
            UnitPrice=F('OrderingDetailId__DetailUnitPrice'),
        ).filter(
            Q(OrderingId__SlipDiv='S') | 
            Q(OrderingId__SlipDiv='T') | 
            Q(OrderingId__SlipDiv='M') | 
            Q(OrderingId__SlipDiv='N') | 
            Q(OrderingId__SlipDiv='W') ,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(search_date[0]),str(search_date[1])),
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return ReciveStock

#出庫
def GetIssueStock(search_date,OrderInput):
    IssueStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'id',
        'ResultItemNumber',
        ).annotate(
            Issue_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='P') | 
            Q(OrderingId__SlipDiv='I') | 
            Q(OrderingId__SlipDiv='E') | 
            Q(OrderingId__SlipDiv='D') | 
            Q(OrderingId__SlipDiv='B') ,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(search_date[0]),str(search_date[1])),
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return IssueStock

#加工数
def GetStockProcess(search_date,OrderInput):
    StockProcess = RequestResult.objects.values(
        'id',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            Process=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250924 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(search_date[0]),str(search_date[1])),
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return StockProcess