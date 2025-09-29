from myapp.models import RequestResult, Inventory
# 検索機能のために追加
from django.db.models import Q, Max, Sum, F
# 計算用
from django.db.models import Sum

#在庫一覧
def GetCarryFowardRecord():
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
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_Record

#加工在庫一覧
def GetCarryForwardProcess():
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
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') | 
            Q(OrderingId__SlipDiv='X'),
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingDetailId__is_Stock=1,
            BacklogOrderDiv=0,
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_Process

#繰越入庫
def GetCarryForwardReciveStock(search_date):
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
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_ReciveStock

#繰越出庫
def GetCarryForwardIssue(search_date):
    CarryForward_Issue = RequestResult.objects.values(
        'id',
        'OrderingId__OrderNumber',
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
            ResultDate__lt=str(search_date[0]),
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return CarryForward_Issue

#繰越加工
def GetCarryForwardProcessStock(search_date):
    CarryForward_ProcessStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ProcessStock_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
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
def GetCarryForwardInventory():
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
            ).order_by(
                'OrderNumber'
                )

    return CarryForward_Inventory

#入庫
def GetReciveStock(search_date):
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
            ).order_by(
                'OrderingId__OrderNumber'
                )
    return ReciveStock

#出庫
def GetIssueStock(search_date):
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
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return IssueStock

#加工数
def GetStockProcess(search_date):
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
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
            Q(OrderingId__SlipDiv='X'),
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__StockDiv=0,
            ResultDate__range=(str(search_date[0]),str(search_date[1])),
            ).order_by(
                'OrderingId__OrderNumber'
                )

    return StockProcess

def carryforward(table_param, Start_date, End_date, DuPrice, PrPrice, Item):
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
            #Q(OrderingId__SlipDiv='K') | 
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
            #2025-08-04 追加
            ResultItemNumber=Item,
            ).order_by(
                'ResultDate'
                )

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
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
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

    CarryForward_Records=[]
    for d in CarryForward_Record:
        CarryForward_Records.append(d)

    for d in CarryForward_Process:
        CarryForward_Records.append(d)

    #繰越入庫
    CarryForward_ReciveStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        ).annotate(
            ReciveStock_total=Sum('ShippingVolume')
        ).filter(
            #Q(OrderingId__SlipDiv='K') | 
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

    #繰越出庫
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

    #繰越加工
    CarryForward_ProcessStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        ).annotate(
            ProcessStock_total=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
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

    #2025-07-15 追加 調整残高
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

    #繰越残高計算
    CarryForward_Stock=[]   
    firstLoop = True
    for q in CarryForward_Records:
        OrderNumber=q['OrderingId__OrderNumber']
        total=q['CarryForward_total']
        Process_total=q['Process_total']
        #2025-07-15
        InventoryVol_total=0
        ManufacturingVol_total=0
        CarryForward_Stock.append(q)

        if firstLoop:
            for t in CarryForward_ReciveStock:
                OrderNumberReciveStock=t['OrderingId__OrderNumber']
                if(OrderNumber==OrderNumberReciveStock):
                    total=total+t['ReciveStock_total'] 
                    q['CarryForward_total']=total
            for dt in CarryForward_Issue:
                OrderNumberIssue=dt['OrderingId__OrderNumber']
                if(OrderNumber==OrderNumberIssue):
                    total=total-dt['Issue_total']
                    q['CarryForward_total']=total
            for tbl in CarryForward_ProcessStock:
                OrderNumberProcess=tbl['OrderingId__OrderNumber']
                if(OrderNumber==OrderNumberProcess):
                    Process_total=Process_total+tbl['ProcessStock_total']
                    q['Process_total']=Process_total
            for Invent in CarryForward_Inventory:
                OrderNumberInventory=Invent['OrderNumber']
                if(OrderNumber==OrderNumberInventory):
                    # 在庫数量
                    InventoryVol_total=InventoryVol_total+Invent['InventoryVol_total']
                    q['InventoryVol_total']=InventoryVol_total
                    # 在庫金額
                    InventoryPrice_total=Invent['InventoryPrice_total']
                    q['InventoryPrice_total']=int(InventoryPrice_total)
                    # 加工数量
                    ManufacturingVol_total=ManufacturingVol_total+Invent['ManufacturingVol_total']
                    q['Process_total']=ManufacturingVol_total
                    q['ManufacturingVol_total']=ManufacturingVol_total
                    # 加工単価
                    if Invent['ManufacturingPrice_total']!=0 and ManufacturingVol_total!=0:
                        ManufacturingPrice_total=Invent['ManufacturingPrice_total']
                        q['ManufacturingPrice_total']=int(ManufacturingPrice_total)
                        q['ProcessingUnitprice']=int(ManufacturingPrice_total)


            if total!=0:
                q['ResultDate'] = Start_date
                
            firstLoop = False

    #入庫
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
    #出庫数
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

    #加工数
    StockProcess = RequestResult.objects.values(
        'id',
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        ).annotate(
            Process=Sum('ShippingVolume')
        ).filter(
            Q(OrderingId__SlipDiv='F') | 
            Q(OrderingId__SlipDiv='G') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            #20250922 コメントアウト
            #Q(OrderingId__SlipDiv='C') |
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

    #入出庫
    RecieveIssue_Stock=[]
    for q in CarryForward_Stock:
        id=q['id']
        SlipDiv=q['OrderingId__SlipDiv']
        OrderNumber=q['OrderingId__OrderNumber']
        RecieveIssue_Stock.append(q)
        #入庫数
        for t in ReciveStock:
            idRecive=t['id']
            SlipDivRecive=t['OrderingId__SlipDiv']
            OrderNumberRecive=t['OrderingId__OrderNumber']
            if(OrderNumber==OrderNumberRecive) and (SlipDiv==SlipDivRecive) and (id==idRecive):              
                q['ReciveStock'] = t['Recive']
        #出庫数
        for dt in StockIssue:
            idIssue=dt['id']
            SlipDivIssue=dt['OrderingId__SlipDiv']
            OrderNumberIssue=dt['OrderingId__OrderNumber']
            if(OrderNumber==OrderNumberIssue) and (SlipDiv==SlipDivIssue) and (id==idIssue):
                q['Issue'] = dt['Issue']
        #加工数
        for dat in StockProcess:
            idProcess=dat['id']
            SlipDivProcess=dat['OrderingId__SlipDiv']
            OrderNumberProcess=dat['OrderingId__OrderNumber']
            if(OrderNumber==OrderNumberProcess) and (SlipDiv==SlipDivProcess) and (id==idProcess):
                q['Process'] = dat['Process']        

    #残数量の計算
    Remaining_Stock=[]
    firstLoop = True
    for q in RecieveIssue_Stock:
        if firstLoop:
            #繰越数量
            Remaining = q['CarryForward_total'] + q['ReciveStock'] - q['Issue']
            #仕入金額残
            UnitPrice = int(DuPrice) * Remaining
            #繰越加工数
            ProcessStock = q['Process_total'] + q['Process']
            #加工金額
            ProcessPrice = int(PrPrice) * ProcessStock
            #残金額
            Balance = int(UnitPrice) + int(ProcessPrice) 
            firstLoop = False            
        else:
            #繰越数量
            Remaining = Remaining + q['ReciveStock'] - q['Issue']
            #仕入金額残
            UnitPrice = int(DuPrice) * Remaining  
            #繰越加工数
            ProcessStock = q['Process_total'] + q['Process']
            #加工金額
            ProcessPrice = int(PrPrice) * ProcessStock
            #残金額
            Balance = int(UnitPrice) + int(ProcessPrice) 

        q['Remaining'] = Remaining
        q['DetailUnitPrice'] = int(UnitPrice)
        q['ProcessingUnitprice'] = ProcessPrice
        q['Balance'] = Balance

        Remaining_Stock.append(q)

    Remaining=[]
    result=0
    for tbl in Remaining_Stock:
        result = tbl['CarryForward_total'] + tbl['ReciveStock'] + tbl['Issue'] + tbl['Process']
        if result!=0:
            Remaining.append(tbl)
        result = 0

    return Remaining

if __name__ == '__main__':
    carryforward()
