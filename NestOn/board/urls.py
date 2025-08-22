from django.urls import path
from .views import (
    post_category_list_view,
    post_list_create_view,
    post_detail_manage_view,
    comment_create_view,
    comment_manage_view,
    post_like_view,
    report_post_view,
    hot_posts_view,
    my_posts_view,
    my_comments_view,
    reported_posts_view,
)

urlpatterns = [
    # 카테고리
    path('posts/categories/', post_category_list_view, name='post-category-list'),
    
    # 게시글
    path('posts/', post_list_create_view, name='post-list-create'),
    path('posts/hot/', hot_posts_view, name='hot-posts'),
    path('posts/my/', my_posts_view, name='my-posts'),
    path('posts/<int:post_id>/', post_detail_manage_view, name='post-detail-manage'),
    
    # 댓글
    path('posts/<int:post_id>/comments/', comment_create_view, name='comment-create'),
    path('comments/my/', my_comments_view, name='my-comments'),
    path('comments/<int:comment_id>/', comment_manage_view, name='comment-manage'),

    # 상호작용
    path('posts/<int:post_id>/like/', post_like_view, name='post-like'),
    path('posts/<int:post_id>/report/', report_post_view, name='post-report'),

    # 관리자
    path('admin/reports/', reported_posts_view, name='reported-posts'),
]