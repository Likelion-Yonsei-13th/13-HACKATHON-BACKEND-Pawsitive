from django.db import models
from User.models import Category # User 앱의 Category 모델을 가져옵니다.

class LocalEvent(models.Model):
    api_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    
    start_date = models.DateTimeField(null=True, blank=True) # 기존 필드도 null 허용
    end_date = models.DateTimeField(null=True, blank=True)   # 기존 필드도 null 허용
    location_name = models.CharField(max_length=100)
    place = models.CharField(max_length=255, null=True, blank=True) # 새 필드
    image_url = models.URLField(max_length=500, blank=True, null=True)
    org_link = models.URLField(max_length=500, blank=True, null=True) # 새 필드
    
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    recommendation_score = models.IntegerField(default=70)

    def __str__(self):
        return self.title
    
class CommercialArea(models.Model):
    """ 서울시 실시간 상권 정보를 저장하는 모델 """
    area_nm = models.CharField(max_length=100) # AREA_NM (핫스팟 장소명)
    area_cd = models.CharField(max_length=100, unique=True) # AREA_CD (핫스팟 코드)
    
    # 정렬에 필요한 필드
    rsb_sh_payment_cnt = models.IntegerField(default=0) # RSB_SH_PAYMENT_CNT (업종 실시간 신한카드 결제 건수)
    cmrcl_10_rate = models.FloatField(default=0.0) # 10대 소비율
    cmrcl_20_rate = models.FloatField(default=0.0) # 20대 소비율
    cmrcl_30_rate = models.FloatField(default=0.0) # 30대 소비율
    cmrcl_40_rate = models.FloatField(default=0.0) # 40대 소비율
    cmrcl_50_rate = models.FloatField(default=0.0) # 50대 소비율
    cmrcl_60_rate = models.FloatField(default=0.0) # 60대 이상 소비율

    # 그 외 프론트엔드에 전달할 필드들
    live_cmrcl_stts = models.CharField(max_length=100, null=True, blank=True)
    area_cmrcl_lvl = models.CharField(max_length=100, null=True, blank=True)
    area_sh_payment_cnt = models.IntegerField(default=0)
    rsb_lrg_ctgr = models.CharField(max_length=100, null=True, blank=True)
    rsb_mid_ctgr = models.CharField(max_length=100, null=True, blank=True)
    rsb_payment_lvl = models.CharField(max_length=100, null=True, blank=True)
    rsb_mct_time = models.CharField(max_length=100, null=True, blank=True)
    cmrcl_male_rate = models.FloatField(default=0.0)
    cmrcl_female_rate = models.FloatField(default=0.0)
    cmrcl_personal_rate = models.FloatField(default=0.0)
    cmrcl_time = models.CharField(max_length=100, null=True, blank=True)
    
    # 제외될 필드 (DB에는 저장)
    area_sh_payment_amt_min = models.IntegerField(default=0)
    area_sh_payment_amt_max = models.IntegerField(default=0)
    rsb_sh_payment_amt_min = models.IntegerField(default=0)
    rsb_sh_payment_amt_max = models.IntegerField(default=0)
    cmrcl_corporation_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.area_nm