from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.session_id}"

    class Meta:
        ordering = ['-created_at']

class ChatMessage(models.Model):
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

class BotResponse(models.Model):
    keyword = models.CharField(max_length=100)
    response = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.keyword}: {self.response[:50]}..."

    class Meta:
        ordering = ['keyword']
