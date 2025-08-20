from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import (
    # 공공 데이터 소식
    PublicDataNews, PublicDataNewsRead,
    # 제보 데이터 소식
    ReportDataNews, ReportDataComment, ReportDataLike, ReportDataReport,
    # 지역행사 (기존 유지)
    LocalEvent, LocalEventComment, LocalEventLike, LocalEventInterest, EventSubscription
)
from .serializers import (
    # 공공 데이터 소식 Serializer
    PublicDataNewsSerializer,
    # 제보 데이터 소식 Serializer
    ReportDataNewsListSerializer, ReportDataNewsDetailSerializer, ReportDataNewsCreateSerializer, ReportDataNewsUpdateSerializer,
    ReportDataCommentSerializer, ReportDataCommentCreateSerializer, ReportDataLikeSerializer, ReportDataReportSerializer,
    # 지역행사 Serializer (기존 유지)
    LocalEventListSerializer, LocalEventDetailSerializer, LocalEventCommentCreateSerializer
)
from .services import PublicNewsService, LocalEventService
from User.models import Location, Category, SubCategory
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import json

# ========================================
# 0. 메인 화면
# ========================================

def main_view(request):
    """NestOn 메인 화면"""
    return render(request, 'board/main.html')

# ========================================
# 1. 커뮤니티 게시판 (사용자 작성)
# ========================================

# 커뮤니티 게시글 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def community_post_list_view(request):
    """커뮤니티 게시글 목록 조회 API"""
    try:
        # 쿼리 파라미터 처리
        location_id = request.query_params.get('location_id')
        category_id = request.query_params.get('category_id')
        subcategory_id = request.query_params.get('subcategory_id')
        search = request.query_params.get('search', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 기본 쿼리셋 (활성화된 게시글만)
        queryset = CommunityPost.objects.filter(is_active=True)
        
        # 지역 필터링
        if location_id:
            try:
                location = Location.objects.get(id=location_id)
                queryset = queryset.filter(location=location)
            except Location.DoesNotExist:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "존재하지 않는 지역입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 카테고리 필터링
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "존재하지 않는 카테고리입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 서브카테고리 필터링
        if subcategory_id:
            try:
                subcategory = SubCategory.objects.get(id=subcategory_id)
                queryset = queryset.filter(subcategory=subcategory)
            except SubCategory.DoesNotExist:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "존재하지 않는 서브카테고리입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 검색 필터링
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        posts = queryset[start:end]
        
        # 직렬화
        serializer = CommunityPostListSerializer(posts, many=True, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "커뮤니티 게시글 목록 조회 성공",
            "data": {
                "posts": serializer.data,
                "total_count": queryset.count(),
                "page": page,
                "page_size": page_size
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 게시글 상세 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def community_post_detail_view(request, post_id):
    """커뮤니티 게시글 상세 조회 API"""
    try:
        post = get_object_or_404(CommunityPost, id=post_id, is_active=True)
        
        # 조회수 증가
        post.increase_view_count()
        
        # 직렬화
        serializer = CommunityPostDetailSerializer(post, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "커뮤니티 게시글 상세 조회 성공",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except CommunityPost.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 게시글입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 게시글 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def community_post_create_view(request):
    """커뮤니티 게시글 작성 API"""
    try:
        serializer = CommunityPostCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        
        return Response({
            "status": 201,
            "success": True,
            "message": "커뮤니티 게시글이 성공적으로 작성되었습니다.",
            "data": {
                "post_id": post.id
            }
        }, status=status.HTTP_201_CREATED)
        
    except serializers.ValidationError as e:
        error_message = next(iter(e.detail.values()))[0] if e.detail else "입력 데이터가 올바르지 않습니다."
        return Response({
            "status": 400,
            "success": False,
            "message": error_message,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 게시글 수정
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def community_post_update_view(request, post_id):
    """커뮤니티 게시글 수정 API"""
    try:
        post = get_object_or_404(CommunityPost, id=post_id, is_active=True)
        
        # 작성자 확인
        if post.author != request.user:
            return Response({
                "status": 403,
                "success": False,
                "message": "게시글을 수정할 권한이 없습니다.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommunityPostUpdateSerializer(post, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "status": 200,
            "success": True,
            "message": "커뮤니티 게시글이 성공적으로 수정되었습니다.",
            "data": None
        }, status=status.HTTP_200_OK)
        
    except CommunityPost.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 게시글입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
        error_message = next(iter(e.detail.values()))[0] if e.detail else "입력 데이터가 올바르지 않습니다."
        return Response({
            "status": 400,
            "success": False,
            "message": error_message,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 게시글 삭제
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def community_post_delete_view(request, post_id):
    """커뮤니티 게시글 삭제 API"""
    try:
        post = get_object_or_404(CommunityPost, id=post_id, is_active=True)
        
        # 작성자 확인
        if post.author != request.user:
            return Response({
                "status": 403,
                "success": False,
                "message": "게시글을 삭제할 권한이 없습니다.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 소프트 삭제 (is_active = False)
        post.is_active = False
        post.save()
        
        return Response({
            "status": 200,
            "success": True,
            "message": "커뮤니티 게시글이 성공적으로 삭제되었습니다.",
            "data": None
        }, status=status.HTTP_200_OK)
        
    except CommunityPost.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 게시글입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 댓글 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def community_comment_create_view(request, post_id):
    """커뮤니티 댓글 작성 API"""
    try:
        post = get_object_or_404(CommunityPost, id=post_id, is_active=True)
        
        serializer = CommunityCommentCreateSerializer(
            data=request.data, 
            context={'request': request, 'post_id': post_id}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        return Response({
            "status": 201,
            "success": True,
            "message": "커뮤니티 댓글이 성공적으로 작성되었습니다.",
            "data": {
                "comment_id": comment.id
            }
        }, status=status.HTTP_201_CREATED)
        
    except CommunityPost.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 게시글입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
        error_message = next(iter(e.detail.values()))[0] if e.detail else "입력 데이터가 올바르지 않습니다."
        return Response({
            "status": 400,
            "success": False,
            "message": error_message,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 게시글 좋아요/취소
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def community_post_like_view(request, post_id):
    """커뮤니티 게시글 좋아요/취소 API"""
    try:
        post = get_object_or_404(CommunityPost, id=post_id, is_active=True)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        existing_like = CommunityPostLike.objects.filter(post=post, user=user).first()
        
        if existing_like:
            # 좋아요 취소
            existing_like.delete()
            message = "좋아요가 취소되었습니다."
            is_liked = False
        else:
            # 좋아요 추가
            CommunityPostLike.objects.create(post=post, user=user)
            message = "좋아요가 추가되었습니다."
            is_liked = True
        
        return Response({
            "status": 200,
            "success": True,
            "message": message,
            "data": {
                "is_liked": is_liked,
                "like_count": post.likes.count()
            }
        }, status=status.HTTP_200_OK)
        
    except CommunityPost.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 게시글입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 커뮤니티 인기 게시글 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def community_popular_posts_view(request):
    """커뮤니티 인기 게시글 조회 API"""
    try:
        location_id = request.query_params.get('location_id')
        limit = int(request.query_params.get('limit', 10))
        
        queryset = CommunityPost.objects.filter(is_active=True)
        
        if location_id:
            try:
                location = Location.objects.get(id=location_id)
                queryset = queryset.filter(location=location)
            except Location.DoesNotExist:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "존재하지 않는 지역입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 조회수와 좋아요 수를 기준으로 정렬
        popular_posts = queryset.annotate(
            like_count=Count('likes')
        ).order_by('-view_count', '-like_count', '-created_at')[:limit]
        
        serializer = CommunityPostListSerializer(popular_posts, many=True, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "커뮤니티 인기 게시글 조회 성공",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================================
# 2. 공공 뉴스 게시판 (구청/시청 API)
# ========================================

# 공공 뉴스 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def public_news_list_view(request):
    """공공 뉴스 목록 조회 API"""
    try:
        # 쿼리 파라미터 처리
        location_id = request.query_params.get('location_id')
        category = request.query_params.get('category')
        source = request.query_params.get('source')
        search = request.query_params.get('search', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        # 기본 쿼리셋
        queryset = PublicNews.objects.filter(is_active=True)
        
        # 지역 필터링
        if location_id:
            try:
                location = Location.objects.get(id=location_id)
                queryset = queryset.filter(location=location)
            except Location.DoesNotExist:
                return Response({
                    "status": 400,
                    "success": False,
                    "message": "존재하지 않는 지역입니다.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 카테고리 필터링
        if category:
            queryset = queryset.filter(category=category)
        
        # 출처 필터링
        if source:
            queryset = queryset.filter(source=source)
        
        # 검색 필터링
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        news_list = queryset[start:end]
        
        # 직렬화
        serializer = PublicNewsListSerializer(news_list, many=True, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "공공 뉴스 목록 조회 성공",
            "data": {
                "news": serializer.data,
                "total_count": queryset.count(),
                "page": page,
                "page_size": page_size
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 공공 뉴스 상세 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def public_news_detail_view(request, news_id):
    """공공 뉴스 상세 조회 API"""
    try:
        news = get_object_or_404(PublicNews, id=news_id, is_active=True)
        
        # 조회수 증가
        news.increase_view_count()
        
        # 직렬화
        serializer = PublicNewsDetailSerializer(news, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "공공 뉴스 상세 조회 성공",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
    except PublicNews.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 뉴스입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 공공 뉴스 댓글 작성
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def public_news_comment_create_view(request, news_id):
    """공공 뉴스 댓글 작성 API"""
    try:
        news = get_object_or_404(PublicNews, id=news_id, is_active=True)
        
        serializer = PublicNewsCommentCreateSerializer(
            data=request.data, 
            context={'request': request, 'news_id': news_id}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        return Response({
            "status": 201,
            "success": True,
            "message": "공공 뉴스 댓글이 성공적으로 작성되었습니다.",
            "data": {
                "comment_id": comment.id
            }
        }, status=status.HTTP_201_CREATED)
        
    except PublicNews.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 뉴스입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except serializers.ValidationError as e:
        error_message = next(iter(e.detail.values()))[0] if e.detail else "입력 데이터가 올바르지 않습니다."
        return Response({
            "status": 400,
            "success": False,
            "message": error_message,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 공공 뉴스 좋아요/취소
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def public_news_like_view(request, news_id):
    """공공 뉴스 좋아요/취소 API"""
    try:
        news = get_object_or_404(PublicNews, id=news_id, is_active=True)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        existing_like = PublicNewsLike.objects.filter(news=news, user=user).first()
        
        if existing_like:
            # 좋아요 취소
            existing_like.delete()
            message = "좋아요가 취소되었습니다."
            is_liked = False
        else:
            # 좋아요 추가
            PublicNewsLike.objects.create(news=news, user=user)
            message = "좋아요가 추가되었습니다."
            is_liked = True
        
        return Response({
            "status": 200,
            "success": True,
            "message": message,
            "data": {
                "is_liked": is_liked,
                "like_count": news.likes.count()
            }
        }, status=status.HTTP_200_OK)
        
    except PublicNews.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "존재하지 않는 뉴스입니다.",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 뉴스 구독 설정
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def news_subscription_view(request):
    """뉴스 구독 설정 API"""
    try:
        location_id = request.data.get('location_id')
        category = request.data.get('category')
        is_active = request.data.get('is_active', True)
        
        if not location_id or not category:
            return Response({
                "status": 400,
                "success": False,
                "message": "지역 ID와 카테고리가 필요합니다.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({
                "status": 400,
                "success": False,
                "message": "존재하지 않는 지역입니다.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 구독 설정 생성 또는 업데이트
        subscription, created = NewsSubscription.objects.update_or_create(
            user=request.user,
            location=location,
            category=category,
            defaults={'is_active': is_active}
        )
        
        message = "뉴스 구독이 설정되었습니다." if created else "뉴스 구독이 업데이트되었습니다."
        
        return Response({
            "status": 200,
            "success": True,
            "message": message,
            "data": {
                "subscription_id": subscription.id,
                "is_active": subscription.is_active
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 뉴스 업데이트 (관리자용)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_news_view(request):
    """뉴스 업데이트 API (관리자용)"""
    try:
        # 관리자 권한 확인 (간단한 예시)
        if not request.user.is_staff:
            return Response({
                "status": 403,
                "success": False,
                "message": "관리자 권한이 필요합니다.",
                "data": None
            }, status=status.HTTP_403_FORBIDDEN)
        
        service = PublicNewsService()
        saved_count = service.update_all_news()
        
        return Response({
            "status": 200,
            "success": True,
            "message": f"{saved_count}개의 뉴스가 업데이트되었습니다.",
            "data": {
                "saved_count": saved_count
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========================================
# 3. 지역행사 게시판 Views
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def local_event_list_view(request):
    """지역행사 목록 조회 API"""
    try:
        # 쿼리 파라미터 처리
        page = int(request.GET.get('page', 1))
        location_id = request.GET.get('location')
        category_id = request.GET.get('category')
        status_filter = request.GET.get('status')  # upcoming, ongoing, past
        is_free = request.GET.get('is_free')
        search = request.GET.get('search')
        
        # 기본 쿼리셋
        events = LocalEvent.objects.filter(is_active=True)
        
        # 필터링
        if location_id:
            events = events.filter(location_id=location_id)
        if category_id:
            events = events.filter(category_id=category_id)
        if is_free:
            events = events.filter(is_free=is_free.lower() == 'true')
        if search:
            events = events.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(event_location__icontains=search)
            )
        
        # 상태별 필터링
        now = timezone.now()
        if status_filter == 'upcoming':
            events = events.filter(event_start_date__gt=now)
        elif status_filter == 'ongoing':
            events = events.filter(event_start_date__lte=now, event_end_date__gte=now)
        elif status_filter == 'past':
            events = events.filter(event_end_date__lt=now)
        
        # 정렬 (기본: 시작일 순)
        events = events.order_by('event_start_date')
        
        # 페이지네이션
        paginator = Paginator(events, 10)
        page_obj = paginator.get_page(page)
        
        # 시리얼라이징
        serializer = LocalEventListSerializer(page_obj, many=True, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "지역행사 목록 조회 성공",
            "data": {
                "events": serializer.data,
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous()
            }
        })
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"지역행사 목록 조회 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def local_event_detail_view(request, event_id):
    """지역행사 상세 조회 API"""
    try:
        event = LocalEvent.objects.get(id=event_id, is_active=True)
        
        # 조회수 증가
        event.view_count += 1
        event.save()
        
        serializer = LocalEventDetailSerializer(event, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "지역행사 상세 조회 성공",
            "data": serializer.data
        })
        
    except LocalEvent.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "해당 행사를 찾을 수 없습니다",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"지역행사 상세 조회 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def local_event_comment_create_view(request, event_id):
    """지역행사 댓글 작성 API"""
    try:
        event = LocalEvent.objects.get(id=event_id, is_active=True)
        
        serializer = LocalEventCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                event=event,
                author=request.user
            )
            
            # 댓글 수 업데이트
            event.comment_count = event.comments.filter(is_active=True).count()
            event.save()
            
            return Response({
                "status": 201,
                "success": True,
                "message": "댓글이 성공적으로 작성되었습니다",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": 400,
                "success": False,
                "message": "댓글 작성 실패",
                "data": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except LocalEvent.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "해당 행사를 찾을 수 없습니다",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"댓글 작성 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def local_event_like_view(request, event_id):
    """지역행사 좋아요 API"""
    try:
        event = LocalEvent.objects.get(id=event_id, is_active=True)
        
        # 기존 좋아요 확인
        existing_like = LocalEventLike.objects.filter(event=event, user=request.user).first()
        
        if existing_like:
            # 좋아요 취소
            existing_like.delete()
            event.like_count = max(0, event.like_count - 1)
            event.save()
            
            return Response({
                "status": 200,
                "success": True,
                "message": "좋아요가 취소되었습니다",
                "data": {"liked": False, "like_count": event.like_count}
            })
        else:
            # 좋아요 추가
            LocalEventLike.objects.create(event=event, user=request.user)
            event.like_count += 1
            event.save()
            
            return Response({
                "status": 200,
                "success": True,
                "message": "좋아요가 추가되었습니다",
                "data": {"liked": True, "like_count": event.like_count}
            })
            
    except LocalEvent.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "해당 행사를 찾을 수 없습니다",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"좋아요 처리 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def local_event_interest_view(request, event_id):
    """지역행사 관심 표시 API"""
    try:
        event = LocalEvent.objects.get(id=event_id, is_active=True)
        interest_type = request.data.get('interest_type', 'attend')
        
        # 기존 관심 표시 확인
        existing_interest = LocalEventInterest.objects.filter(event=event, user=request.user).first()
        
        if existing_interest:
            # 관심 유형 업데이트
            existing_interest.interest_type = interest_type
            existing_interest.save()
        else:
            # 새 관심 표시 생성
            LocalEventInterest.objects.create(
                event=event,
                user=request.user,
                interest_type=interest_type
            )
            event.interest_count += 1
            event.save()
        
        return Response({
            "status": 200,
            "success": True,
            "message": "관심 표시가 처리되었습니다",
            "data": {"interest_type": interest_type}
        })
        
    except LocalEvent.DoesNotExist:
        return Response({
            "status": 404,
            "success": False,
            "message": "해당 행사를 찾을 수 없습니다",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"관심 표시 처리 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def event_subscription_view(request):
    """행사 알림 구독 API"""
    try:
        location_id = request.data.get('location')
        category_id = request.data.get('category')
        
        if not location_id:
            return Response({
                "status": 400,
                "success": False,
                "message": "지역 정보가 필요합니다",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 기존 구독 확인
        existing_subscription = EventSubscription.objects.filter(
            user=request.user,
            location_id=location_id
        ).first()
        
        if existing_subscription:
            # 구독 업데이트
            existing_subscription.category_id = category_id
            existing_subscription.save()
            message = "구독이 업데이트되었습니다"
        else:
            # 새 구독 생성
            EventSubscription.objects.create(
                user=request.user,
                location_id=location_id,
                category_id=category_id
            )
            message = "구독이 생성되었습니다"
        
        return Response({
            "status": 200,
            "success": True,
            "message": message,
            "data": None
        })
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"구독 처리 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_events_view(request):
    """행사 데이터 업데이트 API"""
    try:
        service = LocalEventService()
        success = service.update_all_events()
        
        if success:
            return Response({
                "status": 200,
                "success": True,
                "message": "행사 데이터가 성공적으로 업데이트되었습니다",
                "data": None
            })
        else:
            return Response({
                "status": 500,
                "success": False,
                "message": "행사 데이터 업데이트에 실패했습니다",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"행사 데이터 업데이트 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def local_event_featured_view(request):
    """추천 행사 목록 조회 API"""
    try:
        events = LocalEvent.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-event_start_date')[:10]
        
        serializer = LocalEventListSerializer(events, many=True, context={'request': request})
        
        return Response({
            "status": 200,
            "success": True,
            "message": "추천 행사 목록 조회 성공",
            "data": serializer.data
        })
        
    except Exception as e:
        return Response({
            "status": 500,
            "success": False,
            "message": f"추천 행사 목록 조회 실패: {str(e)}",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 웹 페이지 뷰들
def community_board_view(request):
    """커뮤니티 제보 게시판 메인 페이지"""
    return render(request, 'board/community_list.html')

def community_category_view(request, category):
    """카테고리별 제보 목록 페이지"""
    category_display = dict(CommunityPost.CATEGORY_CHOICES).get(category, '기타')
    context = {
        'category': category,
        'category_display': category_display
    }
    return render(request, 'board/community_category.html', context)

def news_board_view(request):
    """공공 뉴스 게시판 웹 페이지"""
    return render(request, 'board/news_list.html')

def public_data_view(request):
    """공공 데이터 소식 메인 페이지"""
    return render(request, 'board/public_data.html')

def public_data_category_view(request, category):
    """공공 데이터 소식 카테고리별 목록 페이지"""
    category_display = dict(PublicDataNews.CATEGORY_CHOICES).get(category, '기타')
    context = {
        'category': category,
        'category_display': category_display
    }
    return render(request, 'board/public_data_category.html', context)

def report_data_view(request):
    """제보 데이터 소식 메인 페이지"""
    return render(request, 'board/community_list.html')

def report_data_category_view(request, category):
    """제보 데이터 소식 카테고리별 목록 페이지"""
    category_display = dict(ReportDataNews.CATEGORY_CHOICES).get(category, '기타')
    context = {
        'category': category,
        'category_display': category_display
    }
    return render(request, 'board/community_category.html', context)

def local_event_board_view(request):
    """나의 지역행사 확인하기 페이지"""
    return render(request, 'board/event_list.html')

def community_post_detail_view_web(request, post_id):
    """커뮤니티 제보 상세 웹 페이지"""
    try:
        post = CommunityPost.objects.get(id=post_id, is_active=True)
        return render(request, 'board/community_detail.html', {'post': post})
    except CommunityPost.DoesNotExist:
        return render(request, 'board/404.html')

def public_data_detail_view_web(request, alert_id):
    """공공 데이터 소식 상세 웹 페이지"""
    try:
        alert = PublicDataNews.objects.get(id=alert_id, is_active=True)
        return render(request, 'board/public_data_detail.html', {'alert': alert})
    except PublicDataNews.DoesNotExist:
        return render(request, 'board/404.html')

def report_data_detail_view_web(request, news_id):
    """제보 데이터 소식 상세 웹 페이지"""
    try:
        news = ReportDataNews.objects.get(id=news_id, is_active=True)
        # 카테고리 표시명 추가
        news.category_display = news.get_category_display()
        return render(request, 'board/report_data_detail.html', {'news': news})
    except ReportDataNews.DoesNotExist:
        return render(request, 'board/404.html')

def local_event_detail_view_web(request, event_id):
    """지역행사 상세 웹 페이지"""
    try:
        event = LocalEvent.objects.get(id=event_id, is_active=True)
        return render(request, 'board/event_detail.html', {'event': event})
    except LocalEvent.DoesNotExist:
        return render(request, 'board/404.html')

# ========================================
# 마이페이지 관련 뷰들
# ========================================
def mypage_view(request):
    """마이페이지 메인"""
    return render(request, 'board/mypage.html')

def myregion_view(request):
    """나의 지역 페이지"""
    return render(request, 'board/myregion.html')

def myinterests_view(request):
    """나의 관심 행사/상권 페이지"""
    return render(request, 'board/myinterests.html')

# ========================================
# 마이페이지 하위 페이지들
# ========================================
def mypage_profile_view(request):
    """개인정보 관리 페이지"""
    return render(request, 'board/mypage_profile.html')

def mypage_notifications_view(request):
    """알림 설정 페이지"""
    return render(request, 'board/mypage_notifications.html')

def mypage_customer_center_view(request):
    """고객센터/운영정책 페이지"""
    return render(request, 'board/mypage_customer_center.html')

def mypage_withdrawal_view(request):
    """탈퇴하기 페이지"""
    return render(request, 'board/mypage_withdrawal.html')

# ========================================
# API 뷰들 - 커뮤니티 제보
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def community_post_list_view(request):
    """커뮤니티 제보 목록 API"""
    try:
        # 필터링
        category = request.GET.get('category')
        location = request.GET.get('location')
        is_urgent = request.GET.get('is_urgent')
        
        posts = CommunityPost.objects.filter(is_active=True)
        
        if category:
            posts = posts.filter(category=category)
        if location:
            posts = posts.filter(location_id=location)
        if is_urgent:
            posts = posts.filter(is_urgent=True)
        
        # 페이지네이션
        paginator = Paginator(posts, 10)
        page = request.GET.get('page', 1)
        posts_page = paginator.get_page(page)
        
        serializer = CommunityPostListSerializer(posts_page, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '제보 목록을 성공적으로 불러왔습니다.',
            'data': {
                'posts': serializer.data,
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': int(page)
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'제보 목록을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def community_category_counts_view(request):
    """카테고리별 제보 수 API"""
    try:
        counts = {}
        for category_code, category_name in CommunityPost.CATEGORY_CHOICES:
            count = CommunityPost.objects.filter(
                category=category_code, 
                is_active=True
            ).count()
            counts[category_code] = count
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '카테고리별 제보 수를 성공적으로 불러왔습니다.',
            'data': counts
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'카테고리별 제보 수를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def community_urgent_posts_view(request):
    """긴급 제보 목록 API"""
    try:
        urgent_posts = CommunityPost.objects.filter(
            is_urgent=True, 
            is_active=True
        ).order_by('-created_at')[:5]
        
        serializer = CommunityPostListSerializer(urgent_posts, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '긴급 제보 목록을 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'긴급 제보 목록을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

# ========================================
# API 뷰들 - 안전안내문자
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def safety_alerts_view(request):
    """안전안내문자 목록 API"""
    try:
        alerts = SafetyAlert.objects.filter(
            is_active=True
        ).order_by('-priority', '-sent_at')[:3]
        
        serializer = SafetyAlertSerializer(alerts, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '안전안내문자를 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'안전안내문자를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

# ========================================
# API 뷰들 - 공공 데이터 소식
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def public_data_list_view(request):
    """공공 데이터 소식 목록 API"""
    try:
        # 필터링
        category = request.GET.get('category')
        location = request.GET.get('location')
        alert_type = request.GET.get('alert_type')
        
        alerts = PublicDataNews.objects.filter(is_active=True)
        
        if category:
            alerts = alerts.filter(category=category)
        if location:
            alerts = alerts.filter(location_id=location)
        if alert_type:
            alerts = alerts.filter(alert_type=alert_type)
        
        # 페이지네이션
        paginator = Paginator(alerts, 10)
        page = request.GET.get('page', 1)
        alerts_page = paginator.get_page(page)
        
        serializer = PublicDataNewsSerializer(alerts_page, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '공공 데이터 소식을 성공적으로 불러왔습니다.',
            'data': {
                'alerts': serializer.data,
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': int(page)
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'공공 데이터 소식을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def public_data_category_counts_view(request):
    """공공 데이터 소식 카테고리별 수 API"""
    try:
        counts = {}
        for category_code, category_name in PublicDataNews.CATEGORY_CHOICES:
            count = PublicDataNews.objects.filter(
                category=category_code, 
                is_active=True
            ).count()
            counts[category_code] = count
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '카테고리별 공공 데이터 소식 수를 성공적으로 불러왔습니다.',
            'data': counts
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'카테고리별 공공 데이터 소식 수를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def public_data_urgent_alerts_view(request):
    """공공 데이터 소식 긴급 안내 API"""
    try:
        urgent_alerts = PublicDataNews.objects.filter(
            alert_type='emergency', 
            is_active=True
        ).order_by('-sent_at')[:5]
        
        serializer = PublicDataNewsSerializer(urgent_alerts, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '긴급 안내를 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'긴급 안내를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

# ========================================
# API 뷰들 - 제보 데이터 소식
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def report_data_list_view(request):
    """제보 데이터 소식 목록 API"""
    try:
        # 필터링
        category = request.GET.get('category')
        location = request.GET.get('location')
        is_urgent = request.GET.get('is_urgent')
        
        news_list = ReportDataNews.objects.filter(is_active=True)
        
        if category:
            news_list = news_list.filter(category=category)
        if location:
            news_list = news_list.filter(location_id=location)
        if is_urgent:
            news_list = news_list.filter(is_urgent=True)
        
        # 페이지네이션
        paginator = Paginator(news_list, 10)
        page = request.GET.get('page', 1)
        news_page = paginator.get_page(page)
        
        serializer = ReportDataNewsListSerializer(news_page, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '제보 데이터 소식을 성공적으로 불러왔습니다.',
            'data': {
                'news': serializer.data,
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': int(page)
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'제보 데이터 소식을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def report_data_category_counts_view(request):
    """제보 데이터 소식 카테고리별 수 API"""
    try:
        counts = {}
        for category_code, category_name in ReportDataNews.CATEGORY_CHOICES:
            count = ReportDataNews.objects.filter(
                category=category_code, 
                is_active=True
            ).count()
            counts[category_code] = count
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '카테고리별 제보 데이터 소식 수를 성공적으로 불러왔습니다.',
            'data': counts
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'카테고리별 제보 데이터 소식 수를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def report_data_urgent_news_view(request):
    """제보 데이터 소식 긴급 제보 API"""
    try:
        urgent_news = ReportDataNews.objects.filter(
            is_urgent=True, 
            is_active=True
        ).order_by('-created_at')[:5]
        
        serializer = ReportDataNewsListSerializer(urgent_news, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '긴급 제보를 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'긴급 제보를 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

# ========================================
# 댓글 관련 API 뷰들
# ========================================
@api_view(['GET'])
@permission_classes([AllowAny])
def report_data_comments_view(request, news_id):
    """제보 데이터 소식 댓글 목록 API"""
    try:
        comments = ReportDataComment.objects.filter(
            news_id=news_id, 
            is_active=True
        ).order_by('-created_at')
        
        serializer = ReportDataCommentSerializer(comments, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '댓글을 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'댓글을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_data_comment_create_view(request, news_id):
    """제보 데이터 소식 댓글 생성 API"""
    try:
        # 댓글 데이터 준비
        comment_data = {
            'content': request.data.get('content'),
            'is_anonymous': request.data.get('is_anonymous', True),
            'parent_id': request.data.get('parent_id')
        }
        
        # 뉴스 존재 확인
        try:
            news = ReportDataNews.objects.get(id=news_id, is_active=True)
        except ReportDataNews.DoesNotExist:
            return Response({
                'status': 'error',
                'success': False,
                'message': '존재하지 않는 제보입니다.',
                'data': None
            }, status=404)
        
        # 시리얼라이저로 댓글 생성
        serializer = ReportDataCommentCreateSerializer(
            data=comment_data,
            context={'request': request, 'news_id': news_id}
        )
        
        if serializer.is_valid():
            comment = serializer.save()
            
            # 뉴스의 댓글 수 업데이트
            news.comment_count = news.comments.filter(is_active=True).count()
            news.save()
            
            return Response({
                'status': 'success',
                'success': True,
                'message': '댓글이 성공적으로 작성되었습니다.',
                'data': ReportDataCommentSerializer(comment).data
            })
        else:
            return Response({
                'status': 'error',
                'success': False,
                'message': '댓글 작성에 실패했습니다.',
                'data': serializer.errors
            }, status=400)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'댓글 작성 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

# ========================================
# 신고 관련 API 뷰들
# ========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_data_report_create_view(request, news_id):
    """제보 데이터 소식 신고 생성 API"""
    try:
        # 신고 데이터 준비
        report_data = {
            'reason': request.data.get('reason'),
            'description': request.data.get('description', '')
        }
        
        # 뉴스 존재 확인
        try:
            news = ReportDataNews.objects.get(id=news_id, is_active=True)
        except ReportDataNews.DoesNotExist:
            return Response({
                'status': 'error',
                'success': False,
                'message': '존재하지 않는 제보입니다.',
                'data': None
            }, status=404)
        
        # 이미 신고했는지 확인
        existing_report = ReportDataReport.objects.filter(
            news_id=news_id,
            reporter=request.user
        ).first()
        
        if existing_report:
            return Response({
                'status': 'error',
                'success': False,
                'message': '이미 신고한 제보입니다.',
                'data': None
            }, status=400)
        
        # 시리얼라이저로 신고 생성
        serializer = ReportDataReportSerializer(
            data=report_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            report = serializer.save()
            
            # 뉴스의 신고 수 업데이트
            news.report_count = news.reports.count()
            news.save()
            
            return Response({
                'status': 'success',
                'success': True,
                'message': '신고가 성공적으로 접수되었습니다.',
                'data': ReportDataReportSerializer(report).data
            })
        else:
            return Response({
                'status': 'error',
                'success': False,
                'message': '신고 접수에 실패했습니다.',
                'data': serializer.errors
            }, status=400)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'신고 접수 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reports_view(request):
    """사용자 신고 내역 API"""
    try:
        reports = ReportDataReport.objects.filter(
            reporter=request.user
        ).order_by('-created_at')
        
        serializer = ReportDataReportSerializer(reports, many=True)
        
        return Response({
            'status': 'success',
            'success': True,
            'message': '신고 내역을 성공적으로 불러왔습니다.',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'신고 내역을 불러오는 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)


# ========================================
# 나의 관심 행사/상권 관련 뷰들
# ========================================

def myinterests_categories_view(request):
    """나의 관심사 카테고리 목록 페이지"""
    try:
        context = {
            'page_title': '관심사 카테고리 목록',
            'page_subtitle': '현재 설정된 관심사 카테고리를 확인하세요'
        }
        return render(request, 'board/myinterests_categories.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


def myinterests_scraps_view(request):
    """나의 스크랩 목록 페이지"""
    try:
        context = {
            'page_title': '스크랩',
            'page_subtitle': '저장한 스크랩을 확인하세요'
        }
        return render(request, 'board/myinterests_scraps.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


def myinterests_change_view(request):
    """나의 관심사 변경 페이지"""
    try:
        context = {
            'page_title': '관심사 변경',
            'page_subtitle': '관심사를 변경하세요'
        }
        return render(request, 'board/myinterests_change.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


# ========================================
# 나의 지역 관련 뷰들
# ========================================

def myregion_residence_view(request):
    """나의 거주지역 설정 페이지"""
    try:
        context = {
            'page_title': '나의 거주지역',
            'page_subtitle': '거주하고 계신 지역을 설정해주세요'
        }
        return render(request, 'board/myregion_residence.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


def myregion_interests_view(request):
    """나의 관심지역 설정 페이지"""
    try:
        context = {
            'page_title': '나의 관심지역',
            'page_subtitle': '관심 있는 지역들을 설정해주세요'
        }
        return render(request, 'board/myregion_interests.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


def myregion_add_view(request):
    """지역 추가 페이지"""
    try:
        context = {
            'page_title': '지역 추가하기',
            'page_subtitle': '새로운 지역을 추가해주세요'
        }
        return render(request, 'board/myregion_add.html', context)
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


# ========================================
# 제보 데이터 카테고리 및 작성 관련 뷰들
# ========================================

def report_data_category_view_web(request, category):
    """제보 데이터 카테고리별 웹 페이지"""
    try:
        # 카테고리 표시명 가져오기
        category_choices = dict(ReportDataNews.CATEGORY_CHOICES)
        category_display = category_choices.get(category, category)
        
        context = {
            'category': category,
            'category_display': category_display
        }
        
        return render(request, 'board/report_data_category.html', context)
        
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


def report_data_create_view_web(request):
    """제보 데이터 작성 웹 페이지"""
    try:
        category = request.GET.get('category', 'other')
        
        # 카테고리 표시명 가져오기
        category_choices = dict(ReportDataNews.CATEGORY_CHOICES)
        category_display = category_choices.get(category, category)
        
        context = {
            'category': category,
            'category_display': category_display
        }
        
        return render(request, 'board/report_data_create.html', context)
        
    except Exception as e:
        return render(request, 'board/error.html', {'error': str(e)})


@api_view(['POST'])
@permission_classes([AllowAny])
def report_data_create_api_view(request):
    """제보 데이터 생성 API"""
    try:
        # 폼 데이터 처리
        data = {
            'title': request.data.get('title'),
            'content': request.data.get('content'),
            'category': request.data.get('category'),
            'location': request.data.get('location', ''),
            'is_anonymous': request.data.get('is_anonymous') == 'on',
            'is_urgent': request.data.get('is_urgent') == 'on',
            'author': request.user.id if request.user.is_authenticated else None
        }
        
        # 이미지 처리
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']
        
        # 시리얼라이저로 제보 생성
        serializer = ReportDataNewsCreateSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            report = serializer.save()
            
            return Response({
                'status': 'success',
                'success': True,
                'message': '제보가 성공적으로 등록되었습니다.',
                'data': ReportDataNewsDetailSerializer(report).data
            })
        else:
            return Response({
                'status': 'error',
                'success': False,
                'message': '제보 등록에 실패했습니다.',
                'data': serializer.errors
            }, status=400)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'success': False,
            'message': f'제보 등록 중 오류가 발생했습니다: {str(e)}',
            'data': None
        }, status=500)
