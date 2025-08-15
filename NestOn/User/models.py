from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return self.username