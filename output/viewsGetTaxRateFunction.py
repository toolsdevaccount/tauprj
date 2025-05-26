from myapp.models import Consumetax
from django.db.models import Q
# メッセージ
#LOG出力設定
import logging
logger = logging.getLogger(__name__)

def gettaxrate():
    gettaxrate = list(Consumetax.objects.values(
        'TaxRate',
        'TaxRateDisplay',
        'TaxStartDate',
        'TaxEndDate'
        ).filter(
            is_Deleted=0
            ).order_by(
                'TaxStartDate'
                ))
    return gettaxrate

def settaxrate(is_taxrate, FromDate, ToDate):
    taxrate=[]
    for dt in is_taxrate:
        dt_startdate = dt['TaxStartDate'].strftime('%Y-%m-%d')
        if dt['TaxEndDate'] == None:
            dt_enddate = '2999-12-31'
        else:
            dt_enddate = dt['TaxEndDate'].strftime('%Y-%m-%d')

        if FromDate >= dt_startdate and ToDate <= dt_enddate:
            taxrate.append(dt['TaxRate'])
            taxrate.append(dt['TaxRateDisplay'])
    return taxrate
