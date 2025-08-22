from django.db import models
from User.models import Category # User 앱의 Category 모델을 가져옵니다.

class LocalEvent(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    # User 앱의 Category 모델과 연결하여 행사를 분류합니다.
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    
    start_date = models.DateField()
    end_date = models.DateField()
    location_name = models.CharField(max_length=100) # 예: '서대문구', '강남구'
    image_url = models.URLField(max_length=500, blank=True)
    
    # 추천순 정렬을 위한 가상 점수 필드
    recommendation_score = models.IntegerField(default=0)

    def __str__(self):
        return self.title