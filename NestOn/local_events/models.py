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