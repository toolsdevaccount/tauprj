from django.shortcuts import redirect
from myapp.models import RequestResult, Inventory
# 検索機能のために追加
from django.db.models import Q, Max, Sum, F
# 計算用
from django.db.models import Sum

def treatment(search_date,OrderInput):
    #在庫一覧
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
            is_Deleted=0, 
            OrderingId__is_Deleted=0, 
            OrderingDetailId__is_Deleted=0,
            OrderingId__StockDiv=0,
            OrderingDetailId__is_Stock=1,
            OrderingId__OrderNumber__in=OrderInput,
            ).order_by(
                'OrderingId__OrderNumber'
                )
    #加工在庫一覧
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
            Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            Q(OrderingId__SlipDiv='C') | 
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

    CarryForward_Records=[]
    for d in CarryForward_Record:
        OrderNumber=d['OrderingId__OrderNumber']
        ResultItemNumber=d['ResultItemNumber']
        CarryForward_Records.append(d)
        for dt in CarryForward_Process:
            if dt['OrderingId__OrderNumber']==OrderNumber and d['ResultItemNumber']==ResultItemNumber:
                d['ProcessingUnitprice'] = int(dt['ProcessingUnitprice'])

    #繰越入庫
    CarryForward_ReciveStock = RequestResult.objects.values(
        'id',
        'OrderingId__OrderNumber',
        'ResultItemNumber',
        ).annotate(
            ReciveStock_total=Sum('ShippingVolume'),
            DetailUnitPrice=F('OrderingDetailId__DetailUnitPrice'),
        ).filter(
            #Q(OrderingId__SlipDiv='K') | 
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

    #繰越出庫
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

    #繰越加工
    CarryForward_ProcessStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'ResultItemNumber',
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

    #調整残高
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

    #繰越残高計算
    CarryForward_Stock=[]   
    for q in CarryForward_Records:
        OrderNumber=q['OrderingId__OrderNumber']
        total=q['CarryForward_total']
        Process_total=q['Process_total']
        ResultItemNumber=q['ResultItemNumber']
        DetailUnitPrice=0
        Process_total=0
        InventoryVol_total=0
        InventoryPrice_total=0
        ManufacturingVol_total=0
        ManufacturingPrice_total=0
        CarryForward_Stock.append(q)

        for t in CarryForward_ReciveStock:
            OrderNumberReciveStock=t['OrderingId__OrderNumber']
            ResultItemNumberReciveStock=t['ResultItemNumber']
            if(OrderNumber==OrderNumberReciveStock) and(ResultItemNumber==ResultItemNumberReciveStock):
                total=total+t['ReciveStock_total'] 
                q['CarryForward_total']=total
                #仕入単価設定
                DetailUnitPrice=t['DetailUnitPrice']
                if DetailUnitPrice!=0 and total!=0:
                    q['DetailUnitPrice']=int(DetailUnitPrice)
                else:
                    q['DetailUnitPrice']=0
        for dt in CarryForward_Issue:
            OrderNumberIssue=dt['OrderingId__OrderNumber']
            ResultItemNumberIssue=dt['ResultItemNumber']
            if(OrderNumber==OrderNumberIssue) and(ResultItemNumber==ResultItemNumberIssue):
                total=total-dt['Issue_total']
                q['CarryForward_total']=total
        for tbl in CarryForward_ProcessStock:
            ResultItemNumberProcess=tbl['ResultItemNumber']
            OrderNumberProcess=tbl['OrderingId__OrderNumber']
            if(OrderNumber==OrderNumberProcess) and(ResultItemNumber==ResultItemNumberProcess):
                Process_total=Process_total+tbl['ProcessStock_total']
                q['Process_total']=Process_total
        #2025-07-15
        for Invent in CarryForward_Inventory:
            OrderNumberInventory=Invent['OrderNumber']
            ResultItemNumberInventory=Invent['ResultItemNumber']
            if(OrderNumber==OrderNumberInventory) and (ResultItemNumber==ResultItemNumberInventory):
                # 在庫数量
                InventoryVol_total=InventoryVol_total+Invent['InventoryVol_total']
                q['CarryForward_total']=InventoryVol_total + total
                q['InventoryVol_total']=InventoryVol_total
                # 在庫金額
                InventoryPrice_total=Invent['InventoryPrice_total']
                q['InventoryPrice_total']=int(InventoryPrice_total)
                if q['DetailUnitPrice']==0:
                    q['DetailUnitPrice']=int(InventoryPrice_total)
                # 加工数量
                ManufacturingVol_total=ManufacturingVol_total+Invent['ManufacturingVol_total']
                q['Process_total']=ManufacturingVol_total + Process_total
                q['ManufacturingVol_total']=ManufacturingVol_total
                # 加工単価
                if Invent['ManufacturingPrice_total']!=0 and ManufacturingVol_total!=0:
                    ManufacturingPrice_total=Invent['ManufacturingPrice_total']
                    q['ManufacturingPrice_total']=int(ManufacturingPrice_total)
                    q['ProcessingUnitprice']=int(ManufacturingPrice_total)

    #入庫
    ReciveStock = RequestResult.objects.values(
        'OrderingId__OrderNumber',
        'id',
        'ResultItemNumber',
        ).annotate(
            Recive_total=Sum('ShippingVolume'),
            UnitPrice=F('OrderingDetailId__DetailUnitPrice'),
        ).filter(
            #Q(OrderingId__SlipDiv='K') | 
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

    #出庫
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

    #加工数
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
            Q(OrderingId__SlipDiv='O') | 
            Q(OrderingId__SlipDiv='H') | 
            Q(OrderingId__SlipDiv='U') | 
            Q(OrderingId__SlipDiv='C') |
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

    #当月入出庫
    Stock_temp=[]
    for q in CarryForward_Stock:
        OrderNumber=q['OrderingId__OrderNumber']
        RecieveStock=q['ReciveStock']
        Issue_total=q['Issue']
        ResultItemNumber=q['ResultItemNumber']
        DetailUnitPrice=0
        Process=0

        Stock_temp.append(q)
        #入庫
        for t in ReciveStock:
            OrderNumberRecive=t['OrderingId__OrderNumber']
            ResultItemNumberRecive=t['ResultItemNumber']
            if(OrderNumber==OrderNumberRecive) and (ResultItemNumber==ResultItemNumberRecive):
                RecieveStock=RecieveStock+t['Recive_total'] 
                q['ReciveStock']=RecieveStock
                #仕入単価設定
                DetailUnitPrice=t['UnitPrice']
                if DetailUnitPrice!=0:
                    q['DetailUnitPrice']=int(DetailUnitPrice)
                else:
                    q['DetailUnitPrice']=int(DetailUnitPrice)
                if q['InventoryPrice_total']!=0:
                    q['DetailUnitPrice']=int(q['InventoryPrice_total'])
        #出庫
        for dt in IssueStock:
            OrderNumberIssue=dt['OrderingId__OrderNumber']
            ResultItemNumberIssue=dt['ResultItemNumber']
            if(OrderNumber==OrderNumberIssue) and (ResultItemNumber==ResultItemNumberIssue):
                Issue_total=Issue_total+dt['Issue_total']
                q['Issue']=Issue_total
        #加工数
        for dat in StockProcess:
            OrderNumberProcess=dat['OrderingId__OrderNumber']
            ResultItemNumberProcess=dat['ResultItemNumber']
            if(OrderNumber==OrderNumberProcess) and (ResultItemNumber==ResultItemNumberProcess):
                Process=Process+dat['Process']
                q['Process'] = Process

    Stock=[]
    result=0
    Remaining=0
    for rec in Stock_temp:
        Remaining = rec['CarryForward_total'] + rec['ReciveStock'] - rec['Issue']
        result = rec['CarryForward_total'] + rec['ReciveStock'] + rec['Issue']
        rec['Remaining'] = Remaining
        if result!=0:
            rec['StockSummary'] = ''           
            Stock.append(rec)
        result = 0

    return Stock

if __name__ == '__main__':
    treatment()
