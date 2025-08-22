from django.urls import path
from .views import category_list_view, alert_list_view

urlpatterns = [
    # 1. 카테고리 목록을 위한 URL
    path('categories/', category_list_view, name='category-list'),
    
    # 2. 상세 목록을 위한 URL (쿼리 파라미터 사용)
    path('alerts/', alert_list_view, name='alert-list'),
]