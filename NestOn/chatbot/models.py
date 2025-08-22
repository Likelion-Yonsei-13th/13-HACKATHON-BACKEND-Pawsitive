from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChatSession(models.Model):
    """챗봇과의 대화 세션을 관리하는 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user.username if self.user else 'Anonymous'}"
    
    class Meta:
        ordering = ['-created_at']

class ChatMessage(models.Model):
    """챗봇과의 개별 메시지를 저장하는 모델"""
    MESSAGE_TYPES = [
        ('user', '사용자'),
        ('bot', '챗봇'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['timestamp']

class BotResponse(models.Model):
    """챗봇의 응답 템플릿을 저장하는 모델"""
    keyword = models.CharField(max_length=100, help_text="트리거 키워드")
    response = models.TextField(help_text="봇 응답 내용")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.keyword}: {self.response[:50]}..."
    
    class Meta:
        ordering = ['keyword']
