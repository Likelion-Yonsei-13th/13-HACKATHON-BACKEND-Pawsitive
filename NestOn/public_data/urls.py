from django.urls import path
from .views import category_list_view, alert_list_view

urlpatterns = [
    # 1. 카테고리 목록을 위한 URL
    path('categories/', category_list_view, name='category-list'),

    # 2. 특정 카테고리의 상세 목록을 위한 URL
    path('alerts/<str:category_key>/', alert_list_view, name='alert-list'),
]