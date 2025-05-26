import datetime
from dateutil import relativedelta
# メッセージ
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

#####################################################################################
#                                月次集計                                        　　#
#####################################################################################
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
#####################################################################################
#                                台帳                                        　　　　#
#####################################################################################
def conversionledger(TargetMonth):
    # 月初、月末を算出する
    tdate = datetime.datetime.strptime(str(TargetMonth), '%Y%m%d')
    startdate = tdate + relativedelta.relativedelta(day=1)
    lastdate = tdate + relativedelta.relativedelta(months=+1,day=1,days=-1)

    # 前月初日、末日を算出する
    Prvstartdate = tdate + relativedelta.relativedelta(months=-1,day=1)
    Prvlastdate = tdate + relativedelta.relativedelta(day=1,days=-1)
    PrtDate = tdate + relativedelta.relativedelta(day=1)

    # 月初
    startdate = startdate.strftime('%Y-%m-%d')
    # 月末
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 前月初日
    Prvstartdate = Prvstartdate.strftime('%Y-%m-%d')
    # 前月末日
    Prvlastdate = Prvlastdate.strftime('%Y-%m-%d')

    #印刷用年月
    PrinttDate = PrtDate.strftime('%Y年%m月')

    #繰越年月日
    CurryDate = PrtDate.strftime('%Y/%m/%d')

    return(startdate, lastdate, Prvstartdate, Prvlastdate, PrinttDate, CurryDate)
#####################################################################################
#                                一括請求書用                                        #
#####################################################################################
def converted(invoiceDate_From, invoiceDate_To, pkclosing):
    # 前月同日を算出する
    if pkclosing==31:
        tdate = datetime.datetime.strptime(str(invoiceDate_From), '%Y%m%d')
        lastdate = tdate - relativedelta.relativedelta(days=1)
    else:
        tdate = datetime.datetime.strptime(str(invoiceDate_To), '%Y%m%d')
        lastdate = tdate - relativedelta.relativedelta(months=1)

    # 文字列を日付に変換する
    invoiceDate_From = datetime.datetime.strptime(str(invoiceDate_From), '%Y%m%d') 
    invoiceDate_To = datetime.datetime.strptime(str(invoiceDate_To), '%Y%m%d')

    # 日付型に変換する
    # 前月同日
    lastdate = lastdate.strftime('%Y-%m-%d')
    # 日付範囲指定From
    Date_From = invoiceDate_From.strftime('%Y-%m-%d') 
    # 日付範囲指定To
    Date_To = invoiceDate_To.strftime('%Y-%m-%d') 
    # 請求日
    billdate = invoiceDate_To.strftime('%Y年%m月%d日')

    return(Date_From, Date_To, lastdate, billdate)
#####################################################################################
#                          依頼先売上、担当者別売上                      　　　        #
#####################################################################################
def convFromTo(TargetMonthFrom, TargetMonthTo):
    # 日付型に変換する
    startdate = datetime.datetime.strptime(str(TargetMonthFrom), '%Y%m%d')
    lastdate =  datetime.datetime.strptime(str(TargetMonthTo), '%Y%m%d')

    # 日付型に変換する(YYYY年mm月dd日用)
    strstart = datetime.datetime.strptime(str(TargetMonthFrom), '%Y%m%d')
    strlast = datetime.datetime.strptime(str(TargetMonthTo), '%Y%m%d')

    # 前月初日、末日を算出する
    # From
    startdate = startdate.strftime('%Y-%m-%d')
    # To
    lastdate = lastdate.strftime('%Y-%m-%d')
    # From(YYYY年mm月dd日用)
    strstart = strstart.strftime('%Y年%m月%d日')
    # To(YYYY年mm月dd日用)
    strlast = strlast.strftime('%Y年%m月%d日')

    return(startdate, lastdate, strstart, strlast)
