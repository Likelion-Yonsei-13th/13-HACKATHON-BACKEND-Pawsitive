from django.db import models

class PublicAlert(models.Model):
    ALERT_CATEGORIES = [
        ('disaster', '자연재해'),
        ('accident', '사고'),
        ('traffic', '교통'),
        ('safety', '치안'),
        ('facility', '시설고장'),
        ('etc', '기타'),
    ]
     # API의 SN(일련번호)를 저장할 필드 추가
    unique_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=ALERT_CATEGORIES)
    published_at = models.DateTimeField(auto_now_add=True)
    location_name = models.CharField(max_length=100)
    source = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
    
class GuardianHouse(models.Model):
    """ 서울시 여성안심지킴이집 정보를 저장하는 모델 """
    brand_name = models.CharField(max_length=255, null=True, blank=True) # BR_NM (브랜드명)
    store_name = models.CharField(max_length=255)      # NM (점포명)
    gu_name = models.CharField(max_length=100)         # GU_NM (자치구)
    address = models.CharField(max_length=500)         # ADDR (주소)

    def __str__(self):
        return self.store_name
    
class CulturalFacility(models.Model):
    """ 서울시 문화공간의 상세 정보를 저장하는 모델 """
    num = models.CharField(max_length=50, unique=True)        # NUM (번호)
    subjcode = models.CharField(max_length=100, null=True, blank=True) # SUBJCODE (주제분류)
    fac_name = models.CharField(max_length=255)               # FAC_NAME (문화시설명)
    address = models.CharField(max_length=500, null=True, blank=True) # ADDR (주소)
    phone = models.CharField(max_length=100, null=True, blank=True)   # PHNE (전화번호)
    fax = models.CharField(max_length=100, null=True, blank=True)     # FAX (팩스번호)
    homepage = models.URLField(max_length=500, null=True, blank=True) # HOMEPAGE (홈페이지)
    open_hour = models.CharField(max_length=255, null=True, blank=True)# OPENHOUR (관람시간)
    entr_fee = models.CharField(max_length=255, null=True, blank=True) # ENTR_FEE (관람료)
    close_day = models.CharField(max_length=255, null=True, blank=True)# CLOSEDAY (휴관일)
    open_day = models.CharField(max_length=255, null=True, blank=True) # OPEN_DAY (개관일자)
    seat_cnt = models.CharField(max_length=100, null=True, blank=True) # SEAT_CNT (객석수)
    main_img = models.URLField(max_length=500, null=True, blank=True)  # MAIN_IMG (대표이미지)
    etc_desc = models.TextField(null=True, blank=True)                # ETC_DESC (기타사항)
    fac_desc = models.TextField(null=True, blank=True)                # FAC_DESC (시설소개)
    entrfree = models.CharField(max_length=50, null=True, blank=True) # ENTRFREE (무료구분)
    subway = models.CharField(max_length=255, null=True, blank=True)  # SUBWAY (지하철)
    busstop = models.CharField(max_length=255, null=True, blank=True) # BUSSTOP (버스정류장)
    airport = models.CharField(max_length=255, null=True, blank=True) # AIRPORT (공항버스)

    def __str__(self):
        return self.fac_name