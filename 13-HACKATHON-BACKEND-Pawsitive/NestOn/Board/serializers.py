from rest_framework import serializers
from .models import (
    # 공공 데이터 소식
    PublicDataNews, PublicDataNewsRead,
    # 제보 데이터 소식
    ReportDataNews, ReportDataComment, ReportDataLike, ReportDataReport,
    # 지역행사 (기존 유지)
    LocalEvent, LocalEventComment, LocalEventInterest, EventSubscription
)
from User.serializers import LocationSerializer, CategorySerializer, SubCategorySerializer
from User.models import Location, Category, SubCategory

# ========================================
# 공공 데이터 소식 Serializer
# ========================================

class PublicDataNewsSerializer(serializers.ModelSerializer):
    get_alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    get_category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = PublicDataNews
        fields = [
            'id', 'title', 'content', 'category', 'get_category_display',
            'alert_type', 'get_alert_type_display', 'sender', 'sender_contact',
            'location', 'is_active', 'is_broadcast', 'priority', 'sent_at', 'expires_at'
        ]

# ========================================
# 제보 데이터 소식 Serializer
# ========================================

class ReportDataNewsListSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author_display_name', read_only=True)
    get_category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = ReportDataNews
        fields = [
            'id', 'title', 'content', 'author_display_name', 'location', 
            'category', 'get_category_display', 'is_anonymous', 'is_verified', 
            'is_urgent', 'image', 'view_count', 'like_count', 'comment_count', 
            'created_at'
        ]

class ReportDataNewsDetailSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author_display_name', read_only=True)
    get_category_display = serializers.CharField(source='get_category_display', read_only=True)
    comments = 'ReportDataCommentSerializer(many=True, read_only=True)'
    
    class Meta:
        model = ReportDataNews
        fields = [
            'id', 'title', 'content', 'author_display_name', 'location', 
            'category', 'get_category_display', 'is_anonymous', 'is_verified', 
            'is_urgent', 'image', 'view_count', 'like_count', 'comment_count', 
            'comments', 'created_at'
        ]

class ReportDataNewsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataNews
        fields = [
            'title', 'content', 'location', 'category', 'is_anonymous', 
            'is_urgent', 'image'
        ]
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class ReportDataNewsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataNews
        fields = [
            'title', 'content', 'location', 'category', 'is_anonymous', 
            'is_urgent', 'image'
        ]

class ReportDataCommentSerializer(serializers.ModelSerializer):
    author_display_name = serializers.CharField(source='author_display_name', read_only=True)
    
    class Meta:
        model = ReportDataComment
        fields = [
            'id', 'content', 'author_display_name', 'parent', 'is_anonymous',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

class ReportDataCommentCreateSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ReportDataComment
        fields = ['content', 'parent_id', 'is_anonymous']
    
    def validate_parent_id(self, value):
        if value is not None:
            try:
                ReportDataComment.objects.get(id=value)
                return value
            except ReportDataComment.DoesNotExist:
                raise serializers.ValidationError("존재하지 않는 부모 댓글입니다.")
        return value
    
    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id:
            validated_data['parent_id'] = parent_id
        
        validated_data['author'] = self.context['request'].user
        validated_data['news_id'] = self.context['news_id']
        return super().create(validated_data)

class ReportDataLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDataLike
        fields = ['id', 'news', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReportDataReportSerializer(serializers.ModelSerializer):
    get_reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    get_status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReportDataReport
        fields = [
            'id', 'news', 'reporter', 'reason', 'get_reason_display',
            'description', 'status', 'get_status_display', 'admin_comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['reporter', 'status', 'admin_comment', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)

# ========================================
# 지역행사 게시판 Serializers (기존 유지)
# ========================================
class LocalEventCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    author_avatar = serializers.CharField(source='author.avatar', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalEventComment
        fields = [
            'id', 'event', 'author', 'author_name', 'author_avatar',
            'content', 'parent', 'is_active', 'created_at', 'created_at_formatted'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

class LocalEventListSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.level2_district', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    event_status = serializers.CharField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    days_until_event = serializers.SerializerMethodField()
    event_start_date_formatted = serializers.SerializerMethodField()
    event_end_date_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalEvent
        fields = [
            'id', 'title', 'content', 'location', 'location_name',
            'category', 'category_name', 'subcategory', 'subcategory_name',
            'event_start_date', 'event_end_date', 'event_start_date_formatted', 'event_end_date_formatted',
            'event_location', 'event_address', 'event_fee', 'event_capacity',
            'event_contact', 'event_website', 'event_image', 'event_banner',
            'source', 'view_count', 'like_count', 'comment_count', 'interest_count',
            'is_active', 'is_featured', 'is_free', 'event_status',
            'is_ongoing', 'is_upcoming', 'is_past', 'days_until_event',
            'created_at', 'published_at'
        ]
    
    def get_days_until_event(self, obj):
        """행사까지 남은 일수 계산"""
        from django.utils import timezone
        now = timezone.now()
        if obj.event_start_date > now:
            delta = obj.event_start_date - now
            return delta.days
        return 0
    
    def get_event_start_date_formatted(self, obj):
        return obj.event_start_date.strftime('%Y-%m-%d %H:%M')
    
    def get_event_end_date_formatted(self, obj):
        return obj.event_end_date.strftime('%Y-%m-%d %H:%M')

class LocalEventDetailSerializer(LocalEventListSerializer):
    comments = LocalEventCommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    user_interest = serializers.SerializerMethodField()
    
    class Meta(LocalEventListSerializer.Meta):
        fields = LocalEventListSerializer.Meta.fields + [
            'comments', 'is_liked', 'user_interest', 'api_data'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_user_interest(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            interest = obj.interests.filter(user=request.user).first()
            if interest:
                return {
                    'type': interest.interest_type,
                    'display': interest.get_interest_type_display()
                }
        return None

class LocalEventCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalEventComment
        fields = ['event', 'content', 'parent']
        read_only_fields = ['author']

class LocalEventInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalEventInterest
        fields = ['event', 'interest_type']
        read_only_fields = ['user']

class EventSubscriptionSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.level2_district', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = EventSubscription
        fields = [
            'id', 'location', 'location_name', 'category', 'category_name',
            'notify_new_events', 'notify_reminder', 'notify_free_events',
            'created_at'
        ]
        read_only_fields = ['user', 'created_at']
