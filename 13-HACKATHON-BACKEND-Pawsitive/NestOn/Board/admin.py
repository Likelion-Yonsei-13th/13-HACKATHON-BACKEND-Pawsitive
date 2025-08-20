from django.contrib import admin
from .models import (
    # 공공 데이터 소식
    PublicDataNews, PublicDataNewsRead,
    # 제보 데이터 소식
    ReportDataNews, ReportDataComment, ReportDataLike, ReportDataReport,
    # 지역행사 (기존 유지)
    LocalEvent, LocalEventComment, LocalEventLike, LocalEventInterest, EventSubscription
)

# ========================================
# 1. 공공 데이터 소식 관리
# ========================================

@admin.register(PublicDataNews)
class PublicDataNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'category', 'alert_type', 'location', 'is_active', 'is_broadcast', 'sent_at']
    list_filter = ['category', 'alert_type', 'is_active', 'is_broadcast', 'sent_at', 'location']
    search_fields = ['title', 'content', 'sender', 'location__level2_district']
    list_editable = ['is_active', 'is_broadcast']
    readonly_fields = ['sent_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'category', 'alert_type')
        }),
        ('발송 정보', {
            'fields': ('sender', 'sender_contact', 'location', 'is_broadcast')
        }),
        ('우선순위 및 만료', {
            'fields': ('priority', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('상태', {
            'fields': ('is_active', 'sent_at')
        }),
    )

@admin.register(PublicDataNewsRead)
class PublicDataNewsReadAdmin(admin.ModelAdmin):
    list_display = ['news', 'user', 'read_at']
    list_filter = ['read_at', 'news__category', 'news__location']
    search_fields = ['news__title', 'user__name', 'user__username']
    readonly_fields = ['read_at']

# ========================================
# 2. 제보 데이터 소식 관리
# ========================================

@admin.register(ReportDataNews)
class ReportDataNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_display_name', 'location', 'category', 'is_verified', 'is_urgent', 'report_count', 'created_at', 'is_active']
    list_filter = ['category', 'is_verified', 'is_urgent', 'is_anonymous', 'is_active', 'created_at', 'location']
    search_fields = ['title', 'content', 'author__name', 'author__username', 'location__level2_district']
    list_editable = ['is_verified', 'is_urgent', 'is_active']
    readonly_fields = ['view_count', 'like_count', 'comment_count', 'report_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'author', 'location', 'category')
        }),
        ('제보 설정', {
            'fields': ('is_anonymous', 'is_urgent', 'image')
        }),
        ('검증 및 신고', {
            'fields': ('is_verified', 'report_count'),
            'classes': ('collapse',)
        }),
        ('통계', {
            'fields': ('view_count', 'like_count', 'comment_count'),
            'classes': ('collapse',)
        }),
        ('상태', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(ReportDataComment)
class ReportDataCommentAdmin(admin.ModelAdmin):
    list_display = ['content', 'author_display_name', 'news', 'parent', 'is_anonymous', 'created_at', 'is_active']
    list_filter = ['is_anonymous', 'is_active', 'created_at', 'news__location']
    search_fields = ['content', 'author__name', 'author__username', 'news__title']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ReportDataLike)
class ReportDataLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'news', 'created_at']
    list_filter = ['created_at', 'news__location']
    search_fields = ['user__name', 'user__username', 'news__title']
    readonly_fields = ['created_at']

@admin.register(ReportDataReport)
class ReportDataReportAdmin(admin.ModelAdmin):
    list_display = ['news', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at', 'news__location']
    search_fields = ['news__title', 'reporter__name', 'reporter__username', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('신고 정보', {
            'fields': ('news', 'reporter', 'reason', 'description')
        }),
        ('처리 정보', {
            'fields': ('status', 'admin_comment')
        }),
        ('시간', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ========================================
# 3. 지역행사 게시판 Admin (기존 유지)
# ========================================
@admin.register(LocalEvent)
class LocalEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'location', 'category', 'event_start_date', 'event_end_date',
        'event_location', 'event_fee', 'is_free', 'is_featured', 'is_active',
        'view_count', 'like_count', 'comment_count', 'interest_count'
    ]
    list_filter = [
        'location', 'category', 'is_free', 'is_featured', 'is_active',
        'event_start_date', 'event_end_date', 'source'
    ]
    search_fields = ['title', 'content', 'event_location', 'event_address']
    readonly_fields = ['view_count', 'like_count', 'comment_count', 'interest_count']
    date_hierarchy = 'event_start_date'
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'location', 'category', 'subcategory')
        }),
        ('행사 정보', {
            'fields': (
                'event_start_date', 'event_end_date', 'event_location', 'event_address',
                'event_fee', 'event_capacity', 'event_contact', 'event_website'
            )
        }),
        ('미디어', {
            'fields': ('event_image', 'event_banner'),
            'classes': ('collapse',)
        }),
        ('API 정보', {
            'fields': ('source', 'source_id', 'api_data'),
            'classes': ('collapse',)
        }),
        ('통계', {
            'fields': ('view_count', 'like_count', 'comment_count', 'interest_count'),
            'classes': ('collapse',)
        }),
        ('상태', {
            'fields': ('is_active', 'is_featured', 'is_free')
        }),
        ('시간', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LocalEventComment)
class LocalEventCommentAdmin(admin.ModelAdmin):
    list_display = ['event', 'author', 'content', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'event']
    search_fields = ['content', 'author__name', 'event__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(LocalEventLike)
class LocalEventLikeAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'created_at']
    list_filter = ['created_at', 'event']
    search_fields = ['event__title', 'user__name']
    readonly_fields = ['created_at']

@admin.register(LocalEventInterest)
class LocalEventInterestAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'interest_type', 'created_at']
    list_filter = ['interest_type', 'created_at', 'event']
    search_fields = ['event__title', 'user__name']
    readonly_fields = ['created_at']

@admin.register(EventSubscription)
class EventSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'category', 'notify_new_events', 'notify_reminder', 'notify_free_events', 'created_at']
    list_filter = ['notify_new_events', 'notify_reminder', 'notify_free_events', 'created_at', 'location']
    search_fields = ['user__name', 'location__level2_district']
    readonly_fields = ['created_at', 'updated_at']
