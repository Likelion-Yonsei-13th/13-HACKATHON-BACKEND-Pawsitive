from django.contrib import admin
from .models import ChatSession, ChatMessage, BotResponse

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']

@admin.register(BotResponse)
class BotResponseAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'response', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['keyword', 'response']
    readonly_fields = ['created_at']
