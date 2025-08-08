from myapp.models import RequestResult, Inventory
# 検索機能のために追加
from django.db.models import Q, Max, Sum

#在庫一覧
def GetCarryforwardRecord(table_param, Item):
    CarryForward_Record = RequestResult.objects.values(
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        'ResultDate',
        'id',
        ).annotate(
            ProductName=Max('OrderingId__ProductName'),
            OrderingCount=Max('OrderingId__OrderingCount'),
            RequestCustomer=Max('OrderingId__RequestCode_id__CustomerName'),       
            ShippingCustomer=Max('OrderingId__ShippingCode_id__CustomerName'),
            DetailColor=Max('OrderingDetailId__DetailColor'),
            DetailUnitPrice=Max(0),
            CarryForward_total=Max(0),
            ReciveStock=Max(0),
            Issue=Max(0),
            Remaining=Max(0),
            Process_total=Max(0),
            Process=Max(0),
            Balance=Max(0),
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
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__StockDiv=0,
            ResultItemNumber=Item,
            ).order_by(
                'ResultDate'
                )

    return CarryForward_Record

#加工在庫一覧
def GetCarryforwardProcess(table_param, Item):
    CarryForward_Process = RequestResult.objects.values(
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        'ResultDate',
        'id',
        ).annotate(
            ProductName=Max('OrderingId__ProductName'),
            OrderingCount=Max('OrderingId__OrderingCount'),
            RequestCustomer=Max('OrderingId__RequestCode_id__CustomerName'),       
            ShippingCustomer=Max('OrderingId__ShippingCode_id__CustomerName'),
            DetailColor=Max('OrderingDetailId__DetailColor'),
            DetailUnitPrice=Max(0),
            CarryForward_total=Max(0),
            ReciveStock=Max(0),
            Issue=Max(0),
            Remaining=Max(0),
            Process_total=Max(0),
            Process=Max(0),
            Balance=Max(0),
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__StockDiv=0,
            ResultItemNumber=Item,
            ).order_by(
                'ResultDate'
                )

    return CarryForward_Process

#繰越入庫
def GetCarryforwardReciveStock(table_param, Start_date, Item):
    CarryForward_ReciveStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        ).annotate(
            ReciveStock_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='S') | 
            Q(OrderingId__SlipDiv='T') | 
            Q(OrderingId__SlipDiv='M') | 
            Q(OrderingId__SlipDiv='N') | 
            Q(OrderingId__SlipDiv='W') ,
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(Start_date),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_ReciveStock

#繰越出庫
def GetCarryforwardIssue(table_param, Start_date, Item):
    CarryForward_Issue = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        ).annotate(
            Issue_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='P') | 
            Q(OrderingId__SlipDiv='I') | 
            Q(OrderingId__SlipDiv='E') | 
            Q(OrderingId__SlipDiv='D') | 
            Q(OrderingId__SlipDiv='B') ,
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(Start_date),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )
    
    return CarryForward_Issue

#繰越加工
def GetCarryforwardProcessStock(table_param, Start_date, Item):
    CarryForward_ProcessStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        ).annotate(
            ProcessStock_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__lt=str(Start_date),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_ProcessStock

#調整残高
def GetCarryforwardInventory(table_param, Item):
    CarryForward_Inventory = Inventory.objects.values(
        'OrderNumber'
        ).annotate(
            InventoryVol_total=Sum('InventoryVol'),
            InventoryPrice_total=Sum('InventoryPrice'),
            ManufacturingVol_total=Sum('ManufacturingVol'),
            ManufacturingPrice_total=Sum('ManufacturingPrice'),
        ).filter(
            is_Deleted=0,
            OrderNumber=table_param,
            ResultItemNumber=Item,
            ).order_by(
                'OrderNumber'
                )
    return CarryForward_Inventory

#入庫
def GetReciveStock(table_param, Start_date, End_date, Item):
    ReciveStock = RequestResult.objects.values(
        'id',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        ).annotate(
            Recive=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='S') | 
            Q(OrderingId__SlipDiv='T') | 
            Q(OrderingId__SlipDiv='M') | 
            Q(OrderingId__SlipDiv='N') | 
            Q(OrderingId__SlipDiv='W') ,
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(Start_date),str(End_date)),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return ReciveStock

#出庫数
def GetStockIssue(table_param, Start_date, End_date, Item):
    StockIssue = RequestResult.objects.values(
        'id',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        ).annotate(
            Issue=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='P') | 
            Q(OrderingId__SlipDiv='I') | 
            Q(OrderingId__SlipDiv='E') | 
            Q(OrderingId__SlipDiv='D') | 
            Q(OrderingId__SlipDiv='B') ,
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(Start_date),str(End_date)),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return StockIssue

#加工数
def GetStockProcess(table_param, Start_date, End_date, Item):
    StockProcess = RequestResult.objects.values(
        'id',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        ).annotate(
            Process=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            OrderingId__OrderNumber=table_param,
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            ResultDate__range=(str(Start_date),str(End_date)),
            ResultItemNumber=Item,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return StockProcess