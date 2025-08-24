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