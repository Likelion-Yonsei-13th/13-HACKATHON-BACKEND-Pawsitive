from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .models import Post, Comment, Like
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, CommentCreateUpdateSerializer
)

# 1. 게시글 목록 조회 및 생성
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list_create_view(request):
    if request.method == 'GET':
        posts = Post.objects.filter(is_active=True) 
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostCreateUpdateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            post = serializer.save(author=request.user)
            return Response(PostDetailSerializer(post, context={'request': request}).data, status=status.HTTP_201_CREATED)

# 2. 게시글 상세 조회, 수정, 삭제
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail_manage_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # --- 접근 권한 확인 로직 추가 ---
    # 글이 비활성 상태이고, 요청한 사용자가 글쓴이가 아닐 경우
    # (추가: 관리자도 볼 수 있게 하려면 and not request.user.is_staff 추가)
    if not post.is_active and post.author != request.user:
        return Response({"error": "삭제되었거나 비공개 처리된 게시글입니다."}, status=status.HTTP_404_NOT_FOUND)
    # --------------------------------

    if request.method == 'GET':
        post.view_count += 1
        post.save()
        serializer = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)

    # 작성자 본인만 수정/삭제 가능
    if post.author != request.user:
        return Response({"message": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        serializer = PostCreateUpdateSerializer(post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_post = serializer.save()
            return Response(PostDetailSerializer(updated_post, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response({"message": "게시글이 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)


# 3. 댓글 생성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = CommentCreateUpdateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 4. 댓글 수정, 삭제
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

# 5. 핫글 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def hot_posts_view(request):
    try:
        posts = Post.objects.annotate(like_count=Count('likes')).filter(like_count__gte=30).order_by('-created_at')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    except Exception as e:
        # 서버 오류 발생 시 500 에러와 메시지 반환
        return Response({"error": "핫 게시글을 불러오는 데 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 6. 내가 쓴 글 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_posts_view(request):
    posts = Post.objects.filter(author=request.user)
    serializer = PostListSerializer(posts, many=True)
    return Response(serializer.data)

# 7. 내가 쓴 댓글 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_comments_view(request):
    comments = Comment.objects.filter(author=request.user)
    serializer = CommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data)


# 8. 게시글 좋아요 / 좋아요 취소
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # 이미 좋아요를 눌렀는지 확인
    existing_like = Like.objects.filter(post=post, user=user).first()

    if existing_like:
        # 이미 좋아요를 눌렀다면 -> 좋아요 취소 (DELETE)
        existing_like.delete()
        is_liked = False
        message = "좋아요가 취소되었습니다."
    else:
        # 좋아요를 누르지 않았다면 -> 좋아요 추가 (CREATE)
        Like.objects.create(post=post, user=user)
        is_liked = True
        message = "좋아요를 추가했습니다."
        
    like_count = post.likes.count()

    return Response({
        "message": message,
        "is_liked": is_liked,
        "like_count": like_count
    })

# 9. 게시글 신고 (기존 함수를 아래 내용으로 교체)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = ReportSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        if Report.objects.filter(post=post, reporter=request.user).exists():
            return Response({"message": "이미 신고한 게시글입니다."}, status=status.HTTP_409_CONFLICT)
        
        serializer.save(reporter=request.user, post=post)

        # --- 자동 블라인드 로직 시작 ---
        report_count = Report.objects.filter(post=post).count()
        if report_count >= 20:
            post.is_active = False
            post.save()
            # (선택사항) 관리자에게 알림을 보내는 로직 추가 가능
        # --- 자동 블라인드 로직 끝 ---

        return Response({"message": "신고가 정상적으로 접수되었습니다."}, status=status.HTTP_201_CREATED)
    
# 10 .관리자용 - 신고 10건 이상 게시글 목록 조회
@api_view(['GET'])
@permission_classes([IsAdminUser]) # 관리자만 접근 가능
def reported_posts_view(request):
    # 각 게시글별로 신고 횟수를 세고, 10회 이상인 것만 필터링
    reported_posts = Post.objects.annotate(report_count=Count('reports')).filter(report_count__gte=10)
    
    # PostListSerializer를 재사용하여 목록 반환
    serializer = PostListSerializer(reported_posts, many=True)
    return Response(serializer.data)