from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Post, Comment, Like, Report
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, CommentCreateUpdateSerializer, ReportSerializer
)

# 1. 카테고리 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def post_category_list_view(request):
    categories = Post.CATEGORY_CHOICES
    formatted_categories = [{'key': key, 'name': name} for key, name in categories]
    return Response(formatted_categories)

# 2. 게시글 목록 조회 및 생성
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list_create_view(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        ordering = request.query_params.get('ordering', '-created_at')

        posts = Post.objects.filter(is_active=True)
        
        if category:
            posts = posts.filter(category=category)
        
        if ordering == 'likes':
            posts = posts.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        else:
            posts = posts.order_by('-created_at')

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostCreateUpdateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            post = serializer.save(author=request.user)
            return Response(PostDetailSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)

# 3. 게시글 상세, 수정, 삭제
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail_manage_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not post.is_active and post.author != request.user:
        return Response({"error": "삭제되었거나 비공개 처리된 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        post.view_count += 1
        post.save()
        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)

    if post.author != request.user:
        return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        serializer = PostCreateUpdateSerializer(post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_post = serializer.save()
            return Response(PostDetailSerializer(updated_post, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response({"message": "게시글이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)

# 4. 댓글 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = CommentCreateUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 5. 댓글 수정, 삭제
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_manage_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        serializer = CommentCreateUpdateSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(CommentSerializer(comment, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        comment.delete()
        return Response({"message": "댓글이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)

# 6. 게시글 좋아요 / 좋아요 취소
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return Response({'is_liked': created, 'like_count': post.likes.count()})

# 7. 게시글 신고
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        if Report.objects.filter(post=post, reporter=request.user).exists():
            return Response({"message": "이미 신고한 게시글입니다."}, status=status.HTTP_409_CONFLICT)
        serializer.save(reporter=request.user, post=post)
        report_count = Report.objects.filter(post=post).count()
        if report_count >= 10:
            post.is_active = False
            post.save()
        return Response({"message": "신고가 정상적으로 접수되었습니다."}, status=status.HTTP_201_CREATED)

# 8. 핫글 목록 조회
api_view(['GET'])
@permission_classes([AllowAny])
def hot_posts_view(request):
    try:
        # ✅ URL의 쿼리 파라미터에서 'category' 값을 가져옵니다.
        category = request.query_params.get('category')

        # 기본 쿼리셋: 활성화된 글, 좋아요 30개 이상
        posts = Post.objects.filter(is_active=True).annotate(like_count=Count('likes')).filter(like_count__gte=30)
        
        # ✅ category 값이 있다면, 해당 카테고리로 추가 필터링
        if category:
            posts = posts.filter(category=category)
            
        # 최신순으로 정렬
        posts = posts.order_by('-created_at')
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({"error": "핫 게시글을 불러오는 데 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 9. 내가 쓴 글 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts_view(request):
    posts = Post.objects.filter(author=request.user)
    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)

# 10. 내가 쓴 댓글 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_comments_view(request):
    comments = Comment.objects.filter(author=request.user)
    serializer = CommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data)
    
# 11. 관리자용 신고 목록 조회
@api_view(['GET'])
@permission_classes([IsAdminUser])
def reported_posts_view(request):
    reported_posts = Post.objects.annotate(report_count=Count('reports')).filter(report_count__gte=10)
    serializer = PostListSerializer(reported_posts, many=True)
    return Response(serializer.data)