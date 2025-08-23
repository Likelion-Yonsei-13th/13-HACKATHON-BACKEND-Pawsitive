from django.db import models
from User.models import CustomUser
from public_data.models import PublicAlert # 카테고리 정보를 가져오기 위함

# --- 게시글 모델 ---
class Post(models.Model):
    # PublicAlert 모델의 카테고리 선택지를 그대로 가져와 사용
    CATEGORY_CHOICES = PublicAlert.ALERT_CATEGORIES
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='etc')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True) # 신고 누적 시 False로 변경됨

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'

# --- 댓글 모델 ---
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) # 신고 누적 시 False로 변경됨

    class Meta:
        ordering = ['created_at'] # 항상 작성순으로 정렬

    def __str__(self):
        return f'{self.author.username} on {self.post.title}'

# --- 좋아요 모델 ---
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

# --- 신고 모델 ---
class Report(models.Model):
    REPORT_REASONS = [
        ('false_content', '허위 내용'),
        ('inappropriate', '부적절한 내용'),
        ('spam', '스팸/광고'),
        ('other', '기타'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_posts')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reporter.username} 님이 '{self.post.title}'을 신고"