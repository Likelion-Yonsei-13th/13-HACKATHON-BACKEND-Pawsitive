from django.db import models
from django.contrib.auth import get_user_model
from User.models import Location, Category, SubCategory
from django.utils import timezone

User = get_user_model()

# ========================================
# 1. 공공 데이터 소식 (구청/시청 공식 안내)
# ========================================
class PublicDataNews(models.Model):
    CATEGORY_CHOICES = [
        ('natural_disaster', '자연재해'),
        ('accident', '사고'),
        ('traffic', '교통'),
        ('security', '치안'),
        ('facility', '시설 고장'),
        ('other', '기타'),
    ]
    
    ALERT_TYPES = [
        ('emergency', '긴급'),
        ('warning', '주의'),
        ('info', '안내'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info', verbose_name="알림 유형")
    
    # 발송 기관 정보
    sender = models.CharField(max_length=100, verbose_name="발송 기관")
    sender_contact = models.CharField(max_length=100, blank=True, verbose_name="연락처")
    
    # 지역 정보
    location = models.ForeignKey('User.Location', on_delete=models.CASCADE, verbose_name="대상 지역")
    
    # 알림 설정
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_broadcast = models.BooleanField(default=False, verbose_name="전체 발송")
    priority = models.IntegerField(default=1, verbose_name="우선순위")
    
    # 발송 정보
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="발송일")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="만료일")
    
    class Meta:
        db_table = 'public_data_news'
        verbose_name = '공공 데이터 소식'
        verbose_name_plural = '공공 데이터 소식'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['category', 'location']),
            models.Index(fields=['alert_type', 'sent_at']),
            models.Index(fields=['is_active', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender} - {self.title}"
    
    @property
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

class PublicDataNewsRead(models.Model):
    news = models.ForeignKey(PublicDataNews, on_delete=models.CASCADE, related_name='reads', verbose_name="공공 데이터 소식")
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="사용자")
    read_at = models.DateTimeField(auto_now_add=True, verbose_name="읽은 시간")
    
    class Meta:
        db_table = 'public_data_news_reads'
        verbose_name = '공공 데이터 소식 읽음'
        verbose_name_plural = '공공 데이터 소식 읽음'
        unique_together = ['news', 'user']
        ordering = ['-read_at']
    
    def __str__(self):
        return f"{self.news.title} - {self.user.name}"

# ========================================
# 2. 제보 데이터 소식 (사용자 제보)
# ========================================
class ReportDataNews(models.Model):
    CATEGORY_CHOICES = [
        ('natural_disaster', '자연재해'),
        ('accident', '사고'),
        ('traffic', '교통'),
        ('security', '치안'),
        ('facility', '시설 고장'),
        ('other', '기타'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    author = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="작성자")
    location = models.ForeignKey('User.Location', on_delete=models.CASCADE, verbose_name="지역")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    
    # 제보 관련 필드
    is_anonymous = models.BooleanField(default=True, verbose_name="익명 제보")
    is_verified = models.BooleanField(default=False, verbose_name="검증 완료")
    is_urgent = models.BooleanField(default=False, verbose_name="긴급 제보")
    report_count = models.IntegerField(default=0, verbose_name="신고 수")
    
    # 이미지 관련
    image = models.ImageField(upload_to='report_news/', null=True, blank=True, verbose_name="이미지")
    
    # 통계
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    like_count = models.IntegerField(default=0, verbose_name="좋아요 수")
    comment_count = models.IntegerField(default=0, verbose_name="댓글 수")
    
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        db_table = 'report_data_news'
        verbose_name = '제보 데이터 소식'
        verbose_name_plural = '제보 데이터 소식'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'location']),
            models.Index(fields=['is_urgent', 'created_at']),
            models.Index(fields=['is_verified', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
    
    @property
    def author_display_name(self):
        if self.is_anonymous:
            return "익명"
        return self.author.name

class ReportDataComment(models.Model):
    news = models.ForeignKey(ReportDataNews, on_delete=models.CASCADE, related_name='comments', verbose_name="제보")
    author = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="작성자")
    content = models.TextField(verbose_name="댓글 내용")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="부모 댓글")
    is_anonymous = models.BooleanField(default=True, verbose_name="익명 댓글")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        db_table = 'report_data_comments'
        verbose_name = '제보 댓글'
        verbose_name_plural = '제보 댓글'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.news.title} - {self.author_display_name}"
    
    @property
    def author_display_name(self):
        if self.is_anonymous:
            return "익명"
        return self.author.name

class ReportDataLike(models.Model):
    news = models.ForeignKey(ReportDataNews, on_delete=models.CASCADE, related_name='likes', verbose_name="제보")
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="사용자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 시간")
    
    class Meta:
        db_table = 'report_data_likes'
        verbose_name = '제보 좋아요'
        verbose_name_plural = '제보 좋아요'
        unique_together = ['news', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.news.title} - {self.user.name}"

# ========================================
# 3. 제보 신고 시스템
# ========================================
class ReportDataReport(models.Model):
    REPORT_REASONS = [
        ('false_content', '허위 내용의 글'),
        ('inappropriate', '부적절한 내용'),
        ('spam', '스팸/광고'),
        ('harassment', '욕설/폭력'),
        ('privacy', '개인정보 노출'),
        ('other', '기타'),
    ]
    
    REPORT_STATUS = [
        ('pending', '검토 대기'),
        ('reviewing', '검토 중'),
        ('resolved', '처리 완료'),
        ('rejected', '반려'),
    ]
    
    news = models.ForeignKey(ReportDataNews, on_delete=models.CASCADE, related_name='reports', verbose_name="신고된 제보")
    reporter = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="신고자")
    reason = models.CharField(max_length=20, choices=REPORT_REASONS, verbose_name="신고 사유")
    description = models.TextField(blank=True, verbose_name="상세 설명")
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending', verbose_name="처리 상태")
    
    admin_comment = models.TextField(blank=True, verbose_name="관리자 코멘트")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="신고일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="처리일")
    
    class Meta:
        db_table = 'report_data_reports'
        verbose_name = '제보 신고'
        verbose_name_plural = '제보 신고'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['news', 'reporter']),
        ]
    
    def __str__(self):
        return f"{self.news.title} - {self.get_reason_display()}"


# ========================================
# 2. 공공 뉴스 게시판 (구청/시청 API)
# ========================================

class PublicNews(models.Model):
    """공공기관에서 가져온 지역 소식 모델"""
    SOURCE_CHOICES = [
        ('seoul', '서울시'),
        ('district', '구청'),
        ('data_go_kr', '공공데이터포털'),
        ('other', '기타'),
    ]
    
    CATEGORY_CHOICES = [
        ('notice', '공지사항'),
        ('news', '뉴스'),
        ('event', '행사'),
        ('culture', '문화'),
        ('sports', '체육'),
        ('education', '교육'),
        ('welfare', '복지'),
        ('transport', '교통'),
        ('environment', '환경'),
        ('other', '기타'),
    ]
    
    title = models.CharField(max_length=500, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    summary = models.TextField(blank=True, verbose_name="요약")
    
    # 지역 정보
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='public_news', verbose_name="지역")
    
    # 출처 정보
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="출처")
    source_name = models.CharField(max_length=100, verbose_name="출처명")
    original_url = models.URLField(blank=True, verbose_name="원본 URL")
    external_id = models.CharField(max_length=100, blank=True, verbose_name="외부 ID")
    
    # 카테고리
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    
    # 시간 정보
    published_at = models.DateTimeField(verbose_name="발행일")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="수집일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_important = models.BooleanField(default=False, verbose_name="중요 여부")
    
    # 조회수
    view_count = models.PositiveIntegerField(default=0, verbose_name="조회수")
    
    class Meta:
        ordering = ['-is_important', '-published_at']
        verbose_name = "공공 뉴스"
        verbose_name_plural = "공공 뉴스들"
        unique_together = ['source', 'external_id']
    
    def __str__(self):
        return f"[공공뉴스][{self.location}] {self.title} - {self.source_name}"
    
    def increase_view_count(self):
        """조회수 증가"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class PublicNewsComment(models.Model):
    """공공 뉴스 댓글 모델"""
    news = models.ForeignKey(PublicNews, on_delete=models.CASCADE, related_name='comments', verbose_name="뉴스")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='public_news_comments', verbose_name="작성자")
    content = models.TextField(verbose_name="댓글 내용")
    
    # 부모 댓글 (대댓글 기능)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="부모 댓글")
    
    # 시간 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    # 활성화 여부
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "공공 뉴스 댓글"
        verbose_name_plural = "공공 뉴스 댓글들"
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"


class PublicNewsLike(models.Model):
    """공공 뉴스 좋아요 모델"""
    news = models.ForeignKey(PublicNews, on_delete=models.CASCADE, related_name='likes', verbose_name="뉴스")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='public_news_likes', verbose_name="사용자")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 시간")
    
    class Meta:
        unique_together = ['news', 'user']
        verbose_name = "공공 뉴스 좋아요"
        verbose_name_plural = "공공 뉴스 좋아요들"
    
    def __str__(self):
        return f"{self.user.username}이 {self.news.title}을 좋아함"


class NewsSubscription(models.Model):
    """사용자의 뉴스 구독 설정 모델"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_subscriptions', verbose_name="사용자")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='subscribers', verbose_name="지역")
    category = models.CharField(max_length=20, choices=PublicNews.CATEGORY_CHOICES, verbose_name="카테고리")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="구독일")
    
    class Meta:
        unique_together = ['user', 'location', 'category']
        verbose_name = "뉴스 구독"
        verbose_name_plural = "뉴스 구독들"
    
    def __str__(self):
        return f"{self.user.username} - {self.location} {self.get_category_display()}"


# ========================================
# 3. 지역행사 게시판 (지역별 행사 정보)
# ========================================
class LocalEvent(models.Model):
    """지역행사 모델"""
    title = models.CharField(max_length=200, verbose_name="행사 제목")
    content = models.TextField(verbose_name="행사 내용")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="카테고리")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True, verbose_name="서브카테고리")
    
    # 행사 관련 필드
    event_start_date = models.DateTimeField(verbose_name="행사 시작일")
    event_end_date = models.DateTimeField(verbose_name="행사 종료일")
    event_location = models.CharField(max_length=200, verbose_name="행사 장소")
    event_address = models.CharField(max_length=300, verbose_name="행사 주소")
    event_fee = models.CharField(max_length=100, default="무료", verbose_name="참가비")
    event_capacity = models.IntegerField(null=True, blank=True, verbose_name="참가 인원")
    event_contact = models.CharField(max_length=100, blank=True, verbose_name="연락처")
    event_website = models.URLField(blank=True, verbose_name="행사 웹사이트")
    
    # 이미지 및 첨부파일
    event_image = models.URLField(blank=True, verbose_name="행사 이미지")
    event_banner = models.URLField(blank=True, verbose_name="행사 배너")
    
    # API 관련 필드
    source = models.CharField(max_length=100, verbose_name="데이터 출처")
    source_id = models.CharField(max_length=100, blank=True, verbose_name="원본 ID")
    api_data = models.JSONField(default=dict, verbose_name="API 원본 데이터")
    
    # 통계 필드
    view_count = models.IntegerField(default=0, verbose_name="조회수")
    like_count = models.IntegerField(default=0, verbose_name="좋아요 수")
    comment_count = models.IntegerField(default=0, verbose_name="댓글 수")
    interest_count = models.IntegerField(default=0, verbose_name="관심 표시 수")
    
    # 상태 필드
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    is_featured = models.BooleanField(default=False, verbose_name="추천 행사")
    is_free = models.BooleanField(default=True, verbose_name="무료 행사 여부")
    
    # 시간 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="발행일")
    
    class Meta:
        db_table = 'local_events'
        verbose_name = '지역행사'
        verbose_name_plural = '지역행사'
        ordering = ['-event_start_date', '-created_at']
        indexes = [
            models.Index(fields=['location', 'event_start_date']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    @property
    def is_ongoing(self):
        """현재 진행 중인 행사인지 확인"""
        now = timezone.now()
        return self.event_start_date <= now <= self.event_end_date
    
    @property
    def is_upcoming(self):
        """예정된 행사인지 확인"""
        now = timezone.now()
        return self.event_start_date > now
    
    @property
    def is_past(self):
        """지난 행사인지 확인"""
        now = timezone.now()
        return self.event_end_date < now
    
    @property
    def event_status(self):
        """행사 상태 반환"""
        if self.is_ongoing:
            return "진행중"
        elif self.is_upcoming:
            return "예정"
        else:
            return "종료"

class LocalEventComment(models.Model):
    """지역행사 댓글 모델"""
    event = models.ForeignKey(LocalEvent, on_delete=models.CASCADE, related_name='comments', verbose_name="행사")
    author = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="작성자")
    content = models.TextField(verbose_name="댓글 내용")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="부모 댓글")
    
    # 상태 필드
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    
    # 시간 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        db_table = 'local_event_comments'
        verbose_name = '지역행사 댓글'
        verbose_name_plural = '지역행사 댓글'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.author.name}"

class LocalEventLike(models.Model):
    """지역행사 좋아요 모델"""
    event = models.ForeignKey(LocalEvent, on_delete=models.CASCADE, related_name='likes', verbose_name="행사")
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="사용자")
    
    # 시간 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="좋아요 시간")
    
    class Meta:
        db_table = 'local_event_likes'
        verbose_name = '지역행사 좋아요'
        verbose_name_plural = '지역행사 좋아요'
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.user.name}"

class LocalEventInterest(models.Model):
    """지역행사 관심 표시 모델"""
    event = models.ForeignKey(LocalEvent, on_delete=models.CASCADE, related_name='interests', verbose_name="행사")
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="사용자")
    
    # 관심 유형
    INTEREST_TYPES = [
        ('attend', '참가 예정'),
        ('maybe', '참가 고려'),
        ('share', '공유'),
        ('reminder', '알림 설정'),
    ]
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES, default='attend', verbose_name="관심 유형")
    
    # 시간 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="관심 표시 시간")
    
    class Meta:
        db_table = 'local_event_interests'
        verbose_name = '지역행사 관심'
        verbose_name_plural = '지역행사 관심'
        unique_together = ['event', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event.title} - {self.user.name} ({self.get_interest_type_display()})"

class EventSubscription(models.Model):
    """행사 알림 구독 모델"""
    user = models.ForeignKey('User.CustomUser', on_delete=models.CASCADE, verbose_name="사용자")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="지역")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="카테고리")
    
    # 알림 설정
    notify_new_events = models.BooleanField(default=True, verbose_name="새 행사 알림")
    notify_reminder = models.BooleanField(default=True, verbose_name="행사 전 알림")
    notify_free_events = models.BooleanField(default=True, verbose_name="무료 행사 알림")
    
    # 시간 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="구독 시작일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="구독 수정일")
    
    class Meta:
        db_table = 'event_subscriptions'
        verbose_name = '행사 알림 구독'
        verbose_name_plural = '행사 알림 구독'
        unique_together = ['user', 'location']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.location}"
