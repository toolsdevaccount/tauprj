from myapp.output import viewsGetTaxRateFunction
import datetime
#pandas
import pandas as pd

def GetSalesBalance(SellPrvSum,is_taxrate):
    tax=0
    SellPrvTotal=0
    SellPrvtax=0

    if SellPrvSum:
        #月ごとに売上金額集計-----------------------------------------------#
        tbl_array = []
        for tbl in SellPrvSum:
            tbldate = tbl['monthly']
            tbldate = datetime.date(tbldate.year , tbldate.month, 1)              
            tbl_array.append([tbldate,tbl['Abs_total']])

        dtfrmae = pd.DataFrame(tbl_array)
        prvsalessum = dtfrmae[[0,1]].groupby([0], as_index =False).sum()
        _tuple =  [tuple(x) for x in prvsalessum.values]

        #残高&消費税計算----------------------------------------------------#
        for q in _tuple:
            # 消費税率取得 2025-05-12追加-----------------------------------------------------------------------------------#
            taxrate = viewsGetTaxRateFunction.settaxrate(is_taxrate, q[0].strftime('%Y-%m-%d'), q[0].strftime('%Y-%m-%d'))
            #-------------------------------------------------------------------------------------------------------------#
            SellPrvTotal+=int(q[1])
            tax = int(q[1])
            SellPrvtax+= int(tax * taxrate)
    return(SellPrvTotal, SellPrvtax)
