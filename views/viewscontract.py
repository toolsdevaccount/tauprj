from django.shortcuts import render, redirect
from django.views.generic import ListView 
from myapp.models import CustomerSupplier,OrderingDetail, RequestResult
from django.contrib.auth.mixins import LoginRequiredMixin
from myapp.form.formscontractmanage import ContractManageForm
from myapp.output import exceloutputfunction
from django.contrib.auth import get_user_model

# models
from django.db.models import Q, Sum, Max, Avg
# 日時
from django.utils import timezone
import datetime
from dateutil import relativedelta

# メッセージ
from django.contrib import messages
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

# 受発注一覧/検索
class ContractManageView(LoginRequiredMixin,ListView):
    model = CustomerSupplier
    form_class =  ContractManageForm
    template_name = "crud/contract/list/contractlist.html"

    def get_context_data(self, **kwargs):
        context = super(ContractManageView, self).get_context_data(**kwargs)
        context.update(GetMonth=timezone.now().date() + relativedelta.relativedelta(months=-1))
        context.update(Manager=get_user_model().objects.values('id','first_name', 'last_name'))

        return context

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)

        return queryset

    def List(request, TargetMonth, ManagerCode):
        # データ抽出
        Datatable=treatment(TargetMonth, ManagerCode)

        # listに変換
        Datatable=list(Datatable)

        context = {
            'form': Datatable,
        }

        context.update(GetMonth=timezone.now().date() + relativedelta.relativedelta(months=-1))
        context.update(Manager=get_user_model().objects.values('id','first_name', 'last_name'))

        return render(request, 'crud/contract/list/contractlist.html', context)
   
    def excel_output(request, TargetMonth, ManagerCode):
        search_date = conversion(TargetMonth)
        # データ抽出
        table=treatment(TargetMonth, ManagerCode)

        # listに変換
        table=list(table)

        # 件数確認
        if len(table)==0:
            message = "抽出データありません"
            logger.error(message)
            messages.add_message(request, messages.WARNING, message)
            return redirect("myapp:contract")

        try:
            response = exceloutputfunction.exceloutput(request, table, search_date, ManagerCode)
        except Exception as e:
            message = "Excel作成時にエラーが発生しました"
            logger.error(message)
            messages.add_message(request, messages.ERROR, message)
            return redirect("myapp:contract")

        # 生成したHttpResponseをreturnする
        return response

def conversion(TargetMonth):
    # 月初、月末を算出する
    tdate = datetime.datetime.strptime(str(TargetMonth), '%Y%m%d')
    startdate = tdate + relativedelta.relativedelta(day=1)
    lastdate = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)
    # 月初、月末を算出する(YYYY年mm月dd日用)
    strstart = tdate + relativedelta.relativedelta(day=1)
    strlast = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)
    # 前月初日、末日を算出する
    Prvstartdate = tdate + relativedelta.relativedelta(months=-1,day=1)
    Prvlastdate = tdate + relativedelta.relativedelta(day=1,days=-1)
    # 月初
    startdate = startdate.strftime('%Y-%m-%d')
    # 月末
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 月初(YYYY年mm月dd日用)
    strstart = strstart.strftime('%Y年%m月%d日')
    # 月末(YYYY年mm月dd日用)
    strlast = strlast.strftime('%Y年%m月%d日')
    # 前月初日
    Prvstartdate = Prvstartdate.strftime('%Y-%m-%d')
    # 前月末日
    Prvlastdate = Prvlastdate.strftime('%Y-%m-%d')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, strstart, strlast)

def treatment(TargetMonth, ManagerCode):
    search_date = conversion(TargetMonth)
    #対象年月
    OrderingDate=Q(OrderingTableId__OrderingDate__lte=str(search_date[1]))
    OrderingDateResult=Q(OrderingId__OrderingDate__lte=str(search_date[1]))
    #依頼先
    if ManagerCode!='0':
        Condition_ManagerCode = Q(OrderingTableId__RequestCode_id__ManagerCode=ManagerCode)
        Condition_ManagerCodeResult = Q(OrderingId__RequestCode_id__ManagerCode=ManagerCode)
    else:
        Condition_ManagerCode = Q()
        Condition_ManagerCodeResult = Q()

    OrderDetail = OrderingDetail.objects.values(
            'OrderingTableId__SlipDiv',
            'OrderingTableId__OrderNumber',
            ).annotate(
            Tableid=Max('OrderingTableId__id'),
            id=Max('id'),
            RequestCustomer=Max('OrderingTableId__RequestCode_id__CustomerName'),
            Manager_firstname=Max('OrderingTableId__RequestCode_id__ManagerCode__first_name'),
            Manager_lastname=Max('OrderingTableId__RequestCode_id__ManagerCode__last_name'),
            ProductName=Max('OrderingTableId__ProductName'),
            OrderingCount=Max('OrderingTableId__OrderingCount'),
            DetailVolume=Sum('DetailVolume'),
            DetailUnitPrice=Avg('DetailUnitPrice'),
            PurchasePrice=Max('DetailUnitDiv'),
            DetailSellPrice=Avg('DetailSellPrice'),
            SellPrice=Max('DetailUnitDiv'),
            GrossProfit=Max('DetailUnitDiv'),
            ProcessingUnitPrice=Max(0),
            ProcessingAmount=Max(0),
            ).filter(OrderingDate & 
                    Q(Condition_ManagerCode), 
                    Q(OrderingTableId__SlipDiv="A") | 
                    Q(OrderingTableId__SlipDiv="B") | 
                    Q(OrderingTableId__SlipDiv="S") | 
                    Q(OrderingTableId__SlipDiv="K") ,
                    is_Deleted=0, OrderingTableId__is_Deleted=0,
                    ).order_by(
                        'OrderingTableId__SlipDiv',
                        'OrderingTableId__OrderNumber'                        
                    )
    ResultTotal = RequestResult.objects.values(
        'OrderingId__SlipDiv',
        'OrderingId__OrderNumber',
        ).annotate(
            Shipping_total=Sum('ShippingVolume')
        ).filter(OrderingDateResult & 
                    Q(Condition_ManagerCodeResult), 
                    Q(OrderingId__SlipDiv='A') | 
                    Q(OrderingId__SlipDiv='B') | 
                    Q(OrderingId__SlipDiv='S') | 
                    Q(OrderingId__SlipDiv='K') ,
                    is_Deleted=0, OrderingId__is_Deleted=0, OrderingDetailId__is_Deleted=0,
                    ).order_by(
                    'OrderingId__SlipDiv',
                    'OrderingId__OrderNumber'                        
                    )
    #残高計算
    table=[]
    for q in OrderDetail:
        SlipDiv=q['OrderingTableId__SlipDiv']
        OrderNumber=q['OrderingTableId__OrderNumber']
        total=q['DetailVolume']
        table.append(q)

        for dt in ResultTotal:
            SlipDivResult=dt['OrderingId__SlipDiv']
            OrderNumberResult=dt['OrderingId__OrderNumber']
            if(SlipDiv==SlipDivResult and OrderNumber==OrderNumberResult):
                total=q['DetailVolume'] - dt['Shipping_total']
                # 残高計算値を置き換え
                q['DetailVolume']=total
        # 仕入金額計算
        PuchasePrice=total * q['DetailUnitPrice']
        # 仕入金額を置き換え
        q['PurchasePrice']=PuchasePrice
        # 売上金額計算
        SellPrice=total * q['DetailSellPrice']
        # 売上金額を置き換え
        q['SellPrice']=SellPrice
        # 粗利計算
        GrossProfit=SellPrice - PuchasePrice
        # 粗利金額を置き換え
        q['GrossProfit']=GrossProfit

#--------------------------------------------------------------------------------------------------------------#
    #比較のためコピー
    OrderDetail_row = OrderDetail
    #BとSのオーダーNO両方存在した場合はSの仕入単価、仕入金額をBの加工単価、加工金額にする
    temptable=[]
    TempOrderNumber=[]
    for q in table:
        SlipDiv=q['OrderingTableId__SlipDiv']
        OrderNumber=q['OrderingTableId__OrderNumber']
        total=q['DetailVolume']
        temptable.append(q)
        for d in OrderDetail_row:
            if SlipDiv=="B" and OrderNumber == d['OrderingTableId__OrderNumber'] and d['OrderingTableId__SlipDiv'] == 'S':
                #Bの仕入単価保存
                PUnitPrice=q['DetailUnitPrice']
                #Sの仕入単価をBの仕入単価に設定
                q['DetailUnitPrice']=d['DetailUnitPrice']
                #仕入単価再計算
                UnitPrice=q['DetailUnitPrice'] 
                PuchasePrice=int(total)*int(UnitPrice)
                q['PurchasePrice']=PuchasePrice
                #Bの仕入単価をBの加工単価に設定
                q['ProcessingUnitPrice']=PUnitPrice
                #加工単価計算
                ProcessingAmount=int(total)*int(PUnitPrice)
                q['ProcessingAmount']=ProcessingAmount
                #粗利再計算
                SellPrice=int(q['SellPrice'])
                GrossProfit=SellPrice-PuchasePrice-ProcessingAmount
                q['GrossProfit']=GrossProfit
                TempOrderNumber.append(OrderNumber)
#--------------------------------------------------------------------------------------------------------------#
    #BとSのオーダーNO両方存在した場合はSを削除する
    result=[]
    for q in temptable:
        cnt=0
        OrderNumber=q['OrderingTableId__OrderNumber']
        for d in TempOrderNumber:
            if q['OrderingTableId__SlipDiv']=='S':
                if d==OrderNumber:
                    cnt=1
        if cnt==0:
            result.append(q)               
#--------------------------------------------------------------------------------------------------------------#
    return result
