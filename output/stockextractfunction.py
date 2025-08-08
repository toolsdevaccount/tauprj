from myapp.output import Getstockextractfunction, Getstockextractorderfunction, Getstockextractrowsfunction

def treatment(search_date, OrderNumber):
    if len(OrderNumber)==0:
        #在庫
        CarryForward_Record=Getstockextractfunction.GetCarryFowardRecord()
        #加工在庫
        CarryForward_Process=Getstockextractfunction.GetCarryForwardProcess()
        #入庫繰越分
        CarryForward_ReciveStock=Getstockextractfunction.GetCarryForwardReciveStock(search_date)
        #出庫繰越分
        CarryForward_Issue=Getstockextractfunction.GetCarryForwardIssue(search_date)
        #加工繰越分
        CarryForward_ProcessStock=Getstockextractfunction.GetCarryForwardProcessStock(search_date)
        #残高調整分
        CarryForward_Inventory=Getstockextractfunction.GetCarryForwardInventory()
        #入庫分
        ReciveStock=Getstockextractfunction.GetReciveStock(search_date)
        #出庫分
        IssueStock=Getstockextractfunction.GetIssueStock(search_date)
        #加工分
        StockProcess=Getstockextractfunction.GetStockProcess(search_date)
    else:
        #在庫
        CarryForward_Record=Getstockextractorderfunction.GetCarryFowardRecord(OrderNumber)
        #加工在庫
        CarryForward_Process=Getstockextractorderfunction.GetCarryForwardProcess(OrderNumber)
        #入庫繰越分
        CarryForward_ReciveStock=Getstockextractorderfunction.GetCarryForwardReciveStock(search_date,OrderNumber)
        #出庫繰越分
        CarryForward_Issue=Getstockextractorderfunction.GetCarryForwardIssue(search_date,OrderNumber)
        #加工繰越分
        CarryForward_ProcessStock=Getstockextractorderfunction.GetCarryForwardProcessStock(search_date,OrderNumber)
        #残高調整分
        CarryForward_Inventory=Getstockextractorderfunction.GetCarryForwardInventory(OrderNumber)
        #入庫分
        ReciveStock=Getstockextractorderfunction.GetReciveStock(search_date,OrderNumber)
        #出庫分
        IssueStock=Getstockextractorderfunction.GetIssueStock(search_date,OrderNumber)
        #加工分
        StockProcess=Getstockextractorderfunction.GetStockProcess(search_date,OrderNumber)
    #-----------------------------------------------------------------------------------------------------#
    #加工在庫仕入単価計算
    CarryForward_Records=[]
    for d in CarryForward_Record:
        OrderNumber=d['OrderingId__OrderNumber']
        ResultItemNumber=d['ResultItemNumber']
        CarryForward_Records.append(d)
        for dt in CarryForward_Process:
            if dt['OrderingId__OrderNumber']==OrderNumber and d['ResultItemNumber']==ResultItemNumber:
                d['ProcessingUnitprice'] = int(dt['ProcessingUnitprice'])
    #-----------------------------------------------------------------------------------------------------#
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
            if(OrderNumber==OrderNumberReciveStock and ResultItemNumber==ResultItemNumberReciveStock):
                total=total+t['ReciveStock_total'] 
                q['CarryForward_total']=total
                #仕入単価設定
                DetailUnitPrice=t['DetailUnitPrice']
                if DetailUnitPrice!=0 and total!=0:
                    q['DetailUnitPrice']=int(DetailUnitPrice)
                else:
                    q['DetailUnitPrice']=int(DetailUnitPrice)
        for dt in CarryForward_Issue:
            OrderNumberIssue=dt['OrderingId__OrderNumber']
            ResultItemNumberIssue=dt['ResultItemNumber']
            if(OrderNumber==OrderNumberIssue and ResultItemNumber==ResultItemNumberIssue):
                total=total-dt['Issue_total']
                q['CarryForward_total']=total
        for tbl in CarryForward_ProcessStock:
            OrderNumberProcess=tbl['OrderingId__OrderNumber']
            ResultItemNumberProcess=tbl['ResultItemNumber']
            if(OrderNumber==OrderNumberProcess and ResultItemNumber==ResultItemNumberProcess):
                Process_total=Process_total+tbl['ProcessStock_total']
                q['Process_total']=Process_total
        #繰越残高
        for Invent in CarryForward_Inventory:
            OrderNumberInventory=Invent['OrderNumber']
            ResultItemNumberInventory=Invent['ResultItemNumber']
            if(OrderNumber==OrderNumberInventory) and (ResultItemNumber==ResultItemNumberInventory):
                # 在庫数量
                InventoryVol_total=InventoryVol_total+Invent['InventoryVol_total']
                # 在庫金額
                InventoryPrice_total=Invent['InventoryPrice_total']
                q['InventoryPrice_total']=int(InventoryPrice_total)
                # 2025-08-06
                if q['DetailUnitPrice']==0:
                    q['DetailUnitPrice']=int(InventoryPrice_total)
                # 加工数量
                ManufacturingVol_total=ManufacturingVol_total+Invent['ManufacturingVol_total']
                # 加工単価
                if Invent['ManufacturingPrice_total']!=0 and ManufacturingVol_total!=0:
                    ManufacturingPrice_total=Invent['ManufacturingPrice_total']
                    q['ProcessingUnitprice']=int(ManufacturingPrice_total)
    #-----------------------------------------------------------------------------------------------------#
    #当月入出庫分計算
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
            if(OrderNumber==OrderNumberRecive and ResultItemNumber==ResultItemNumberRecive):
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
            if(OrderNumber==OrderNumberIssue and ResultItemNumber==ResultItemNumberIssue):
                Issue_total=Issue_total+dt['Issue_total']
                q['Issue']=Issue_total
        #加工数
        for dat in StockProcess:
            OrderNumberProcess=dat['OrderingId__OrderNumber']
            ResultItemNumberProcess=dat['ResultItemNumber']
            if(OrderNumber==OrderNumberProcess and ResultItemNumber==ResultItemNumberProcess):
                Process=Process+dat['Process']
                q['Process'] = Process
    #-----------------------------------------------------------------------------------------------------#
    #最終整理
    Stock=[]
    result=0
    Remaining=0
    Balance=0
    for rec in Stock_temp:
        Remaining = rec['CarryForward_total'] + rec['ReciveStock'] - rec['Issue']
        Balance = rec['Process_total'] + rec['Process']
        result = rec['CarryForward_total'] + rec['ReciveStock'] + rec['Issue']
        rec['Remaining'] = Remaining
        rec['Balance'] = Balance
        if result!=0:
            rec['StockSummary'] = ''           
            Stock.append(rec)
        result = 0

    return Stock

def carryforward(table_param, Start_date, End_date, DuPrice, PrPrice, Item):
    #在庫
    CarryForward_Record=Getstockextractrowsfunction.GetCarryforwardRecord(table_param, Item)
    #加工在庫
    CarryForward_Process=Getstockextractrowsfunction.GetCarryforwardProcess(table_param, Item)
    #入庫繰越分
    CarryForward_ReciveStock=Getstockextractrowsfunction.GetCarryforwardReciveStock(table_param, Start_date, Item)
    #出庫繰越分
    CarryForward_Issue=Getstockextractrowsfunction.GetCarryforwardIssue(table_param, Start_date, Item)
    #加工繰越分
    CarryForward_ProcessStock=Getstockextractrowsfunction.GetCarryforwardProcessStock(table_param, Start_date, Item)
    #残高調整分
    CarryForward_Inventory=Getstockextractrowsfunction.GetCarryforwardInventory(table_param, Item)
    #入庫分
    ReciveStock=Getstockextractrowsfunction.GetReciveStock(table_param, Start_date, End_date, Item)
    #出庫分
    StockIssue=Getstockextractrowsfunction.GetStockIssue(table_param, Start_date, End_date, Item)
    #加工分
    StockProcess=Getstockextractrowsfunction.GetStockProcess(table_param, Start_date, End_date, Item)
    #-----------------------------------------------------------------------------------------------------#
    #加工在庫仕入単価計算
    CarryForward_Records=[]
    for d in CarryForward_Record:
        CarryForward_Records.append(d)

    for d in CarryForward_Process:
        CarryForward_Records.append(d)
    #-----------------------------------------------------------------------------------------------------#
    #繰越残高計算
    CarryForward_Stock=[]   
    firstLoop = True
    for q in CarryForward_Records:
        OrderNumber=q['OrderingId__OrderNumber']
        total=q['CarryForward_total']
        Process_total=q['Process_total']
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
    #-----------------------------------------------------------------------------------------------------#
    #当月入出庫分計算
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
    #-----------------------------------------------------------------------------------------------------#
    #最終整理 残数量の計算
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
