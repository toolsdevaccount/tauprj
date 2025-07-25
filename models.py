from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# 日時
from django.utils import timezone
import datetime
# イメージリサイズ
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

import os
from django.core.exceptions import ValidationError
# 全角半角判定
import unicodedata

MAX_SIZE = 2 * 1000 * 1000

# 容量チェック
def validate_max_size(value):
    if value.size > MAX_SIZE:
        raise ValidationError( "ファイルサイズが上限(" + str(MAX_SIZE/1000000) + "MB)を超えています。送信されたファイルサイズ: " + str(value.size/1000000) + "MB")

# 全角チェック
def validate_full_width_character(value):
    charactor = str(value.name)
    text_counter = 0
    for width_character in charactor:
        j = unicodedata.east_asian_width(width_character)
        if 'F' == j:
            text_counter = 1
        elif 'W' == j:
            text_counter = 1
        elif 'A' == j:
            text_counter = 1

    if text_counter == 1:
        raise ValidationError( "ファイル名に全角が含まれています")

# Create your models here.
class prefecture(models.Model):
    prefecturecode = models.CharField(max_length=2,null=False,blank=True,verbose_name="都道府県コード")
    prefecturename = models.CharField(max_length=255,null=False,blank=True,verbose_name="都道府県名")
    blockname = models.CharField(max_length=255,null=False,blank=True,verbose_name="地域名称")

    def __str__(self):
        return str(self.prefecturecode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/customersupplier/customersupplierlist.html')

#2023-11-24 追加（リストから検索するため）
class DivSampleClass(models.Model):
    divcode = models.CharField(max_length=2,null=False,blank=True,verbose_name="区分コード")
    divname = models.CharField(max_length=255,null=False,blank=True,verbose_name="名称")

    def __str__(self):
        return str(self.divcode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/ordering/list/orderinglist.html')

#2023-11-24 追加（リストから検索するため）
class DivOutputClass(models.Model):
    outputdivcode = models.CharField(max_length=2,null=False,blank=True,verbose_name="出力区分コード")
    outputdivname = models.CharField(max_length=255,null=False,blank=True,verbose_name="出力区分名称")

    def __str__(self):
        return str(self.outputdivcode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/ordering/list/orderinglist.html')

#入金支払区分
class DepoPayDiv(models.Model):
    DepoPayDivcode = models.CharField(max_length=2,null=False,blank=True,verbose_name="入金/支払区分コード")
    DepoPayDivname = models.CharField(max_length=255,null=False,blank=True,verbose_name="入金/支払区分名称")

    def __str__(self):
        return str(self.DepoPayDivcode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/Deposit/list/Depositlist.html')

# 得意先仕入先マスター
class CustomerSupplier(models.Model):
    Closing = [
            (0, ""),
            (5, "5日"),
            (10, "10日"),
            (15, "15日"),
            (20, "20日"),
            (25, "25日"),
            (31, "末日"),
        ]
   
    MasterDiv = [
            (0, ""),
            (1, "得意先/仕入先未使用"),
            (2, "得意先"),
            (3, "仕入先"),
            (4, "得意先/仕入先使用"),
        ]
    
    Offset = [
            (0, ""),
            (1, "相殺する"),
            (2, "相殺しない"),
        ]

    ExDepositDiv = [
            (0, ""),
            (1, "現金"),
            (2, "現金以外"),
        ]

    ExDepositMonth = [
            (0, ""),
            (1, "1ヶ月"),
            (2, "2ヶ月"),
            (3, "3ヶ月"),
            (4, "4ヶ月"),
            (5, "5ヶ月"),
            (6, "6ヶ月"),
            (99, "6ヶ月以上"),
        ]

    ExDepositDate = [
            (0, ""),
            (5, "5日"),
            (10, "10日"),
            (15, "15日"),
            (20, "20日"),
            (25, "25日"),
            (31, "末日"),
        ]

    CustomerCode = models.CharField(max_length=6,null=False,verbose_name="コード")
    CustomerName = models.CharField(max_length=30,null=False,blank=True,verbose_name="名称")
    CustomerOmitName = models.CharField(max_length=12,null=False,blank=True,verbose_name="略称")
    CustomerNameKana = models.CharField(max_length=30,null=False,blank=True,verbose_name="カナ")
    Department = models.CharField(max_length=20,null=False,blank=True,default="",verbose_name="部署名")
    PostCode = models.CharField(max_length=8,null=False,blank=True,verbose_name="郵便番号")
    PrefecturesCode = models.ForeignKey(prefecture,on_delete=models.PROTECT,related_name='PrefecturesCode',null=False,default=1,verbose_name="都道府県コード")
    Municipalities = models.CharField(max_length=24,null=False,blank=True,verbose_name="市区町村")
    Address = models.CharField(max_length=24,null=False,blank=True,verbose_name="番地")
    BuildingName = models.CharField(max_length=24,null=False,blank=True,verbose_name="建物名")
    PhoneNumber = models.CharField(max_length=13,null=False,blank=True,verbose_name="電話番号")
    FaxNumber = models.CharField(max_length=12,null=False,blank=True,verbose_name="FAX番号")
    EMAIL = models.EmailField(null=False,blank=True,verbose_name="メールアドレス")
    MasterDiv = models.IntegerField(null=False,default=0,choices=MasterDiv,verbose_name="マスタ区分")
    ClosingDate = models.IntegerField(null=False,default=0,choices=Closing,verbose_name="締日")
    ExDepositMonth = models.IntegerField(null=False,default=0,choices=ExDepositMonth,verbose_name="入金予定月")
    ExDepositDate = models.IntegerField(null=False,default=0,choices=ExDepositDate,verbose_name="入金予定日")
    ExDepositDiv = models.IntegerField(null=False,default=0,choices=ExDepositDiv,verbose_name="入金予定区分")
    ManagerCode = models.ForeignKey(User, to_field='id',on_delete=models.SET_NULL, null=True, db_column='ManagerCode',verbose_name="担当者コード")
    OffsetDiv = models.IntegerField(null=False,default=0,choices=Offset,verbose_name="相殺出力区分")
    LastClaimBalance = models.DecimalField(max_digits=10,decimal_places=0,default=0,null=False,blank=True,verbose_name="前回請求残")
    LastReceivable= models.DecimalField(max_digits=10,decimal_places=0,default=0,null=False,blank=True,verbose_name="前月売掛残")
    LastPayable = models.DecimalField(max_digits=10,decimal_places=0,default=0,null=False,blank=True,verbose_name="前月買掛残")
    LastProceeds = models.DecimalField(max_digits=10,decimal_places=0,default=0,null=False,blank=True,verbose_name="前年売上実績")
    ProceedsTarget = models.DecimalField(max_digits=10,decimal_places=0,default=0,null=False,blank=True,verbose_name="当年売上目標")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.CustomerCode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/customersupplier/customersupplierlist.html')

#受発注テーブル
class OrderingTable(models.Model):
    Title = [
            (0, ""),
            (1, "様"),
            (2, "御中"),
    ]

    SlipDiv = models.CharField(max_length=1,null=False,blank=False,verbose_name="伝票区分")
    OrderNumber = models.CharField(max_length=7,null=False,blank=False,default=0,verbose_name="オーダーNO")
    OrderingDate = models.DateField(null=False,blank=False,default="2000-01-01",verbose_name="依頼日")
    StainShippingDate = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="原糸出荷日")
    ProductName = models.CharField(max_length=24,null=False,blank=True,verbose_name="商品名")
    OrderingCount = models.CharField(max_length=8,null=False,blank=True,verbose_name="番手")
    StainPartNumber = models.CharField(max_length=10,null=False,blank=True,verbose_name="品番")
    StainMixRatio = models.CharField(max_length=20,null=False,blank=True,verbose_name="混率")
    DestinationCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='DestinationCode',null=False,blank=True,verbose_name="手配先コード",default=1)
    SupplierCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='SupplierCode',verbose_name="仕入先コード")
    ShippingCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ShippingCode',verbose_name="出荷先コード")
    CustomeCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='CustomeCode',verbose_name="得意先コード")
    RequestCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='RequestCode',verbose_name="依頼先コード")
    StainShippingCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='StainShippingCode',verbose_name="原糸メーカーコード")
    ApparelCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ApparelCode',verbose_name="アパレルコード",default=1)
    ManagerCode = models.ForeignKey(User, to_field='id',on_delete=models.SET_NULL, null=True, db_column='ManagerCode',verbose_name="担当者コード")
    SupplierPerson = models.CharField(max_length=30,null=False,blank=True,verbose_name="仕入先担当者名")
    TitleDiv = models.IntegerField(null=False,default=0,choices=Title,verbose_name="敬称区分")
    StockDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="在庫済区分")
    MarkName = models.CharField(max_length=20,null=False,blank=True,verbose_name="マーク名")
    OutputDiv = models.ForeignKey(DivOutputClass,on_delete=models.PROTECT,related_name='OutputDivCode',null=False,default=0,verbose_name="出力区分")
    SampleDiv = models.ForeignKey(DivSampleClass,on_delete=models.PROTECT,related_name='DivCode_div',null=False,default=0,verbose_name="サンプル量産区分")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")
    is_Ordered = models.BooleanField(null=False,blank=False,default=False,verbose_name="発注書発行区分")

    # ユニーク制約（以下の組み合わせを一意とする）
    #class Meta:
    #    constraints = [
    #        models.UniqueConstraint(
    #            fields=["SlipDiv", "OrderNumber", "StartItemNumber", "EndItemNumber"],
    #            name="ordernumber_unique"
    #        ),
    #    ]  
   
    def __str__(self):
        return str(self.OrderNumber)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/ordering/orderinglist.html')

# 受発注明細テーブル
class OrderingDetail(models.Model):
    Unit = [
            (0, ""),
            (1, "㎏"),
            (2, "本"),
            (3, "枚"),
            (4, "件"),
        ]
    OrderingTableId = models.ForeignKey(OrderingTable,on_delete=models.PROTECT,blank=True, null=True,related_name='OrderingTableId',verbose_name="受発注テーブルid")
    DetailItemNumber = models.CharField(max_length=4,null=False,blank=False,default=0,verbose_name="項番")
    DetailColorNumber = models.CharField(max_length=8,null=False,blank=True,default=0,verbose_name="色番")
    DetailColor = models.CharField(max_length=16,null=False,blank=True,default=0,verbose_name="カラー")
    DetailTailoring = models.CharField(max_length=1,null=False,blank=True,default=0,verbose_name="仕立")
    DetailVolume = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="数量")
    DetailUnitPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="仕入単価")
    DetailPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="通常単価")
    DetailOverPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="UP分単価")
    DetailSellPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="販売単価")
    DetailSummary = models.TextField(max_length=1000,null=False,blank=True,verbose_name="摘要")
    SpecifyDeliveryDate = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="希望納期")
    StainAnswerDeadline = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="回答納期")
    DeliveryManageDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="納期管理済区分")
    PrintDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="発注書印刷区分")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")
    DetailUnitDiv = models.IntegerField(null=False,default=0,choices=Unit,verbose_name="単位")
    is_Taxation = models.BooleanField(null=False,blank=False,default=True,verbose_name="課税区分")
    is_Stock = models.BooleanField(null=False,blank=False,default=True,verbose_name="在庫区分")

    def __str__(self):
        return str(self.DetailItemNumber)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/ordering/orderinglist.html')
    
# 商品マスター
class Merchandise(models.Model):
    MerchandiseTreatment = [
            (0, ""),
            (1, "通常"),
            (2, "扱停止"),
        ]
    MerchandiseUnitCode = [
        (0, ""),
        (1, "￥"),
        (2, "US$ FOB東京"),
        (3, "US$ FOB上海"),
        (4, "US$ CIF東京"),
        (5, "US$ CIF上海"),
        (6, "US$ CMT東京"),
        (7, "US$ CMT上海"),
        ]
    McdTreatmentCode = models.IntegerField(null=False,default=0,choices=MerchandiseTreatment,verbose_name="扱区分")
    McdTempPartNumber = models.CharField(max_length=20,null=False,blank=True,verbose_name="仮品番")
    McdPartNumber = models.CharField(max_length=20,null=False,blank=False,default=0,verbose_name="本品番")
    McdManagerCode = models.ForeignKey(User, to_field='id',on_delete=models.SET_NULL, null=True, db_column='ManagerCode',verbose_name="担当者コード")
    McdUnitPrice = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="仕入単価")
    McdUnitCode = models.IntegerField(null=False,default=0,choices=MerchandiseUnitCode,verbose_name="仕入単位")
    McdSellPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="販売単価")
    McdProcessfee = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="加工賃")
    McdProcessCode = models.IntegerField(null=False,default=0,choices=MerchandiseUnitCode,verbose_name="加工賃単位")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.McdPartNumber)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/merchandise/merchandiselist.html')

# 商品マスターカラーテーブル
class MerchandiseColor(models.Model):
    McdColorId = models.ForeignKey(Merchandise,on_delete=models.PROTECT,blank=True, null=True,related_name='McdColorId',verbose_name="商品マスタid")
    McdColorNumber = models.CharField(max_length=20,null=False,blank=True,verbose_name="商品カラー番号")
    McdColor = models.CharField(max_length=20,null=False,blank=False,default=0,verbose_name="商品カラー")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.McdColor)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/merchandise/merchandiselist.html')

# 商品マスターサイズテーブル
class MerchandiseSize(models.Model):
    McdSizeId = models.ForeignKey(Merchandise,on_delete=models.PROTECT,blank=True, null=True,related_name='McdSizeId',verbose_name="商品マスタid")
    McdSize = models.CharField(max_length=20,null=False,blank=False,default=0,verbose_name="商品サイズ")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.McdSize)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/merchandise/merchandiselist.html')

#商品マスター明細テーブル
class MerchandiseDetail(models.Model):
    UnitCode = [
        (0, ""),
        (1, "￥"),
        (2, "US$ FOB東京"),
        (3, "US$ FOB上海"),
        (4, "US$ CIF東京"),
        (5, "US$ CIF上海"),
        (6, "US$ CMT東京"),
        (7, "US$ CMT上海"),
    ]  
    McdDtid = models.ForeignKey(Merchandise,on_delete=models.PROTECT,blank=True, null=True,related_name='McdDtid',verbose_name="商品マスタid")
    McdDtProductName = models.CharField(max_length=24,null=False,blank=True,verbose_name="品名")
    McdDtOrderingCount = models.CharField(max_length=8,null=False,blank=True,verbose_name="番手")
    McdDtStainMixRatio = models.CharField(max_length=20,null=False,blank=True,verbose_name="混率")
    McdDtlPrice = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="単価")
    McdDtUnitCode = models.IntegerField(null=False,default=0,choices=UnitCode,verbose_name="単位")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.McdDtid)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/merchandise/merchandiselist.html')

# 商品マスターアップロードファイルテーブル
class MerchandiseFileUpload(models.Model):
    McdDtuploadid = models.ForeignKey(Merchandise, on_delete=models.PROTECT, blank=True, null=True, related_name='McdDtuploadid', verbose_name="商品マスタid")
    uploadPath = models.ImageField(upload_to='photos/%Y/%m/%d',blank=True, null=True, validators=[validate_max_size,validate_full_width_character], verbose_name="アップロードファイルパス")
    middle = ImageSpecField(source='uploadPath', processors=[ResizeToFill(600, 400)],  format="JPEG",  options={'quality': 75})  
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.McdDtuploadid)
    
    def file_name(self):
        return os.path.basename(self.uploadPath.name)

    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/merchandise/merchandiselist.html')

# 製品受発注テーブル
class ProductOrder(models.Model):
    ProductOrderTitleDiv = [
            (0, ""),
            (1, "様"),
            (2, "御中"),
        ]
    ProductOrderMerchandiseCode = models.IntegerField(null=False,default=0,verbose_name="商品コード")
    ProductOrderOrderingDate = models.DateField(null=False,blank=False,default="2000-01-01",verbose_name="発注日")
    ProductOrderManagerCode = models.ForeignKey(User, to_field='id',on_delete=models.SET_NULL, null=True, db_column='ManagerCode',verbose_name="担当者コード")
    ProductOrderSlipDiv = models.CharField(max_length=1,null=False,blank=False,verbose_name="伝票区分")
    ProductOrderOrderNumber = models.CharField(max_length=7,null=False,blank=False,default=0,verbose_name="オーダーNO")
    ProductOrderPartNumber = models.CharField(max_length=20,null=False,blank=False,default=0,verbose_name="本品番")
    ProductOrderApparelCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderApparelCode',verbose_name="アパレルコード")
    ProductOrderDestinationCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderDestinationCode',null=False,blank=True,verbose_name="手配先コード",default=1)
    ProductOrderSupplierCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderSupplierCode',verbose_name="仕入先コード")
    ProductOrderSupplierPerson = models.CharField(max_length=30,null=False,blank=True,verbose_name="仕入先担当者名")
    ProductOrderTitleDiv = models.IntegerField(null=False,default=0,choices=ProductOrderTitleDiv,verbose_name="敬称区分")
    ProductOrderShippingCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderShippingCode',verbose_name="出荷先コード")
    ProductOrderCustomeCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderCustomeCode',verbose_name="得意先コード")
    ProductOrderRequestCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='ProductOrderRequestCode',verbose_name="依頼先コード")
    ProductOrderDeliveryDate = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="納期")
    ProductOrderBrandName = models.CharField(max_length=50,null=False,blank=True,default="",verbose_name="ブランド名")
    ProductOrderMarkName = models.CharField(max_length=20,null=False,blank=True,verbose_name="マーク名")
    ProductOrderSummary = models.TextField(max_length=1000,null=False,blank=True,verbose_name="備考")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")
    is_Ordered = models.BooleanField(null=False,blank=False,default=False,verbose_name="製品発注書発行区分")

    def __str__(self):
        return str(self.ProductOrderMerchandiseCode)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/productorder/list/productorderlist.html')

# 製品受発注明細テーブル
class ProductOrderDetail(models.Model):
    PodDetailId = models.ForeignKey(ProductOrder,on_delete=models.PROTECT,blank=True, null=True,related_name='PodDetailId',verbose_name="製品受発注明細id")
    PodColorId = models.ForeignKey(MerchandiseColor,on_delete=models.PROTECT,blank=True, null=True,related_name='PodColorId',verbose_name="商品カラーid")
    PodSizeId = models.ForeignKey(MerchandiseSize,on_delete=models.PROTECT,blank=True, null=True,related_name='PodSizeId',verbose_name="商品サイズid")
    #2024-10-03 変更
    PodVolume = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False, default=0, verbose_name="数量")
    #PodVolume = models.DecimalField(max_digits=8, decimal_places=0, null=False, blank=False, default=0, verbose_name="数量")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.PodDetailId)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/productorder/list/productorderlist.html')

# 受発注実績テーブル
class RequestResult(models.Model):
    OrderingId = models.ForeignKey(OrderingTable,on_delete=models.PROTECT,blank=True, null=True,related_name='OrderingId',verbose_name="受発注テーブルid")
    OrderingDetailId = models.ForeignKey(OrderingDetail,on_delete=models.PROTECT,blank=True, null=True,related_name='OrderingDetailId',verbose_name="受発注明細id")
    ResultItemNumber = models.CharField(max_length=4,null=False,blank=False,default=0,verbose_name="項番")
    ResultDate = models.DateField(null=False,blank=False,default="2000-01-01",verbose_name="実績日")
    ShippingDate = models.DateField(null=False,blank=False,default="2000-01-01",verbose_name="出荷日")
    ShippingVolume = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="出荷数")
    SlipNumber = models.CharField(max_length=8,null=False,blank=True,verbose_name="伝票番号")
    ResultSummary = models.TextField(max_length=1000,null=False,blank=True,verbose_name="備考")
    ResultMoveDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="移動区分")
    ResultGainDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="目増区分")
    ResultDecreaseDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="目減区分")
    InvoiceIssueDate = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="個別請求書発行日付")
    InvoiceIssueDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="個別請求書発行区分")
    InvoiceNUmber = models.CharField(max_length=6,null=False,blank=True,verbose_name="個別請求書NO")
    SalesTaxRate = models.DecimalField(max_digits=4,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="消費税率")
    OffsetInputDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="相殺入力区分")
    PaymentInputDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="支払入力区分")
    DailyUpdateDate = models.DateField(null=True,blank=True,default="2000-01-01",verbose_name="日次更新日付")
    DailyUpdateDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="日次更新区分")
    DeadlineUpdateDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="締次更新区分")
    MonthlyCustomerDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="得意先月次更新区分")
    MonthlySupplierDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="仕入先月次更新区分")
    BacklogOrderDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="生産発注残区分")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.SlipNumber)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/requestresult/list/requestresultlist.html')

# 入金テーブル
class Deposit(models.Model):
    DepositDate = models.DateField(null=True,blank=True,verbose_name="入金日")
    DepositCustomerCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='DepositCustomerCode',verbose_name="得意先コード")
    DepositMoney = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="入金金額")
    DepositDiv = models.ForeignKey(DepoPayDiv,on_delete=models.PROTECT,related_name='DepositDiv',null=False,default=0,verbose_name="入金区分")
    DepositSummary = models.TextField(max_length=1000,null=False,blank=True,verbose_name="摘要")
    DepositDeadlineUpdateDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="締次更新区分")
    DepositMonthlyUpdateDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="月次更新区分")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.DepositDate)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/Deposit/list/Depositlist.html')

# 支払テーブル
class Payment(models.Model):
    PaymentDate = models.DateField(null=True,blank=True,verbose_name="支払日")
    PaymentSupplierCode = models.ForeignKey(CustomerSupplier,on_delete=models.PROTECT,related_name='PaymentSupplierCode',verbose_name="仕入先コード")
    PaymentMoney = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="支払金額")
    PaymentDiv = models.ForeignKey(DepoPayDiv,on_delete=models.PROTECT,related_name='PaymentDiv',null=False,default=0,verbose_name="支払区分")
    PaymentSummary = models.TextField(max_length=1000,null=False,blank=True,verbose_name="摘要")
    PaymentMonthlyUpdateDiv = models.BooleanField(null=False,blank=False,default=False,verbose_name="月次更新区分")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.DepositDate)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/Payment/list/Paymentlist.html')

# 個別請求書番号管理テーブル
class InvoiceNo(models.Model):
    InvoiceNo = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="個別請求書番号")
    SInvoiceNo = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="染色用個別請求書番号")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")

    def __str__(self):
        return str(self.InvoiceNo)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/DailyUpdate/DailyUpdate.html')

# 消費税率テーブル 2025-05-12追加
class Consumetax(models.Model):
    TaxRate = models.DecimalField(max_digits=4,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="消費税率")
    TaxRateDisplay = models.CharField(max_length=20,null=False,blank=True,verbose_name="税率表示")
    TaxStartDate = models.DateField(null=True,blank=True,verbose_name="税率開始日")
    TaxEndDate = models.DateField(null=True,blank=True,verbose_name="税率終了日")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.TaxRate)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/consumetax/list/consumetaxlist.html')

# 在庫テーブル追加 2025-07-15追加
class Inventory(models.Model):
    OrderNumber = models.CharField(max_length=7,null=False,blank=False,default=0,verbose_name="オーダーNO")
    InventoryVol = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="在庫数残")
    InventoryPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="在庫金額残")
    ManufacturingVol = models.DecimalField(max_digits=8,decimal_places=2, null=False,blank=False,default=0.00,verbose_name="加工数残")
    ManufacturingPrice = models.DecimalField(max_digits=8,decimal_places=0, null=False,blank=False,default=0,verbose_name="加工金額残")
    Created_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="登録者id")
    Updated_id = models.BigIntegerField(null=False,blank=True,default=0,verbose_name="更新者id")
    Created_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="登録日時")
    Updated_at = models.DateTimeField(null=False, blank=False,default=timezone.now() + datetime.timedelta(hours=9),verbose_name="更新日時")
    is_Deleted = models.BooleanField(null=False,blank=False,default=False,verbose_name="削除区分")

    def __str__(self):
        return str(self.OrderNumber)
    # 新規登録・編集完了後のリダイレクト先
    def get_absolute_url(self):
        return reverse('crud/stock/list/stocklist.html')
