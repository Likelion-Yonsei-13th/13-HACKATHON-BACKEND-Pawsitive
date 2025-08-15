# User/urls.py

from django.urls import path
from .views import (
    check_username_view, send_sms_view, verify_sms_view,
    signup_view, login_view,
)

urlpatterns = [
    path('check-username/', check_username_view, name='check-username'),
    path('sms/send/', send_sms_view, name='send-sms'),
    path('sms/verify/', verify_sms_view, name='verify-sms'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
]