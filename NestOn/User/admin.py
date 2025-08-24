# User/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# CustomUser 모델을 관리자 페이지에 등록합니다.
admin.site.register(CustomUser, UserAdmin)
