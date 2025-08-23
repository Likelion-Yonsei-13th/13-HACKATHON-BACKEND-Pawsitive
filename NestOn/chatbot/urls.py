from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # 채팅 인터페이스
    path('', views.chat_view, name='chat'),
    
    # API 엔드포인트들
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/session/create/', views.create_session, name='create_session'),
    path('api/sessions/', views.get_sessions, name='get_sessions'),
    path('api/messages/<str:session_id>/', views.get_messages, name='get_messages'),
]
