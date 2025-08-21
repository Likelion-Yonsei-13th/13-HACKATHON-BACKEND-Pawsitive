from django.urls import path
# views.py 파일에서 필요한 함수들을 직접, 개별적으로 가져옴
from .views import (
    post_list_create_view,
    hot_posts_view,
    my_posts_view,
    post_detail_manage_view,
    comment_create_view,
    my_comments_view,
    comment_manage_view,
    post_like_view,
    reported_posts_view,
    report_post_view,
)

urlpatterns = [
    path('posts/', post_list_create_view, name='post-list-create'),
    path('posts/hot/', hot_posts_view, name='hot-posts'),
    path('posts/my/', my_posts_view, name='my-posts'),
    path('posts/<int:post_id>/', post_detail_manage_view, name='post-detail-manage'),
    path('posts/<int:post_id>/comments/', comment_create_view, name='comment-create'),
    path('comments/my/', my_comments_view, name='my-comments'),
    path('comments/<int:comment_id>/', comment_manage_view, name='comment-manage'),
    path('posts/<int:post_id>/like/', post_like_view, name='post-like'),
    path('posts/<int:post_id>/report/', report_post_view, name='post-report'),
    path('admin/reports/', reported_posts_view, name='reported-posts'),
]