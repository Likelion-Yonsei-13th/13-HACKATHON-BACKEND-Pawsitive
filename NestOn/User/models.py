from django.contrib.auth.models import AbstractUser
from django.db import models


# 1. 지역 모델 새로 추가
class Location(models.Model):
    level1_city = models.CharField(max_length=100)      # 시/도 (예: 경기도)
    level2_district = models.CharField(max_length=100) # 시/군/구 (예: 성남시, 강남구)
    level3_borough = models.CharField(max_length=100, null=True, blank=True) # 일반구 (예: 분당구), 없으면 NULL

    def __str__(self):
        if self.level3_borough:
            return f"{self.level1_city} {self.level2_district} {self.level3_borough}"
        return f"{self.level1_city} {self.level2_district}"

    class Meta:
        # 세 필드의 조합이 항상 고유하도록 설정
        unique_together = ('level1_city', 'level2_district', 'level3_borough')


# 상위 카테고리 (예: 문화.예술, 스포츠.레저)
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# 하위 카테고리 (예: 지역공연, 마라톤.사이클 대회)
class SubCategory(models.Model):
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.parent_category.name} - {self.name}"

class CustomUser(AbstractUser):
    # 회원가입 폼에 필요한 필드
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    birth_date = models.DateField(null=True, blank=True)

    # 약관 동의 필드
    location_services_agreed = models.BooleanField(default=False)
    marketing_push_agreed = models.BooleanField(default=False)
    terms_agreed = models.BooleanField(default=False)
    privacy_agreed = models.BooleanField(default=False)

     # '내 지역' (하나만 선택)
    my_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    
    # '관심 지역' (여러 개 선택 가능)
    interested_locations = models.ManyToManyField(Location, blank=True, related_name='interested_users')

    # 2. interests 필드를 SubCategory와 연결하도록 수정합니다.
    #    (기존에 Interest 모델과 연결했다면, 이제 SubCategory와 연결합니다)
    interests = models.ManyToManyField(SubCategory, blank=True, related_name='users')
    def __str__(self):
        return self.username