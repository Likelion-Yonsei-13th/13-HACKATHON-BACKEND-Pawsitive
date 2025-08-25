# User/urls.py

from django.urls import path
from .views import (
    check_username_view, send_sms_view, verify_sms_view,
    signup_view, login_view,city_list_view,
    district_list_view,
    borough_list_view,
    location_search_view,
    profile_view,
    category_list_view,
    test_token_view,
    test_public_view,
)

urlpatterns = [
    path('check-username/', check_username_view, name='check-username'),
    path('sms/send/', send_sms_view, name='send-sms'),
    path('sms/verify/', verify_sms_view, name='verify-sms'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    
    path('locations/cities/', city_list_view, name='city-list'),
    path('locations/districts/', district_list_view, name='district-list'),
    path('locations/boroughs/', borough_list_view, name='borough-list'),
    path('locations/search/', location_search_view, name='location-search'),
    path('profile/', profile_view, name='profile'),
    path('categories/', category_list_view, name='category-list'),
    
    # 토큰 테스트용 엔드포인트
    path('test-token/', test_token_view, name='test-token'),
    path('test-public/', test_public_view, name='test-public'),
]