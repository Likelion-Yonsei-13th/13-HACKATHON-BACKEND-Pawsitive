import requests
import re
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from User.models import Category
from .models import LocalEvent,CommercialArea
from .serializers import LocalEventSerializer, LocalEventDetailSerializer,CommercialAreaSerializer

def _get_age_group_key(user):
    """ 사용자의 생년월일로 연령대별 소비율 필드 키를 반환하는 함수 """
    if not user.birth_date:
        return 'cmrcl_20_rate' # DB 모델 필드명은 소문자
    
    today = date.today()
    age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
    
    if age < 20: return 'cmrcl_10_rate'
    if age < 30: return 'cmrcl_20_rate'
    if age < 40: return 'cmrcl_30_rate'
    if age < 50: return 'cmrcl_40_rate'
    if age < 60: return 'cmrcl_50_rate'
    return 'cmrcl_60_rate'

def _fetch_shopping_data(user):
    """ '상권.쇼핑' 데이터를 DB에서 조회하고 정렬/직렬화하는 전문가 함수 """
    all_areas = CommercialArea.objects.all()
    age_rate_key = _get_age_group_key(user)

    # 1차: 사용자 연령대 소비율, 2차: 업종 결제 건수 순으로 내림차순 정렬
    sorted_areas = sorted(
        list(all_areas), 
        key=lambda x: (getattr(x, age_rate_key, 0), x.rsb_sh_payment_cnt), 
        reverse=True
    )
    
    serializer = CommercialAreaSerializer(sorted_areas, many=True)
    return serializer.data

def _fetch_db_events(locations, category_name, sort_by, user):
    """ DB에 저장된 행사 데이터를 조회하고 정렬하는 전문가 함수 """
    events_qs = LocalEvent.objects.all()
    if locations:
        location_names = [loc.level2_district for loc in locations]
        events_qs = events_qs.filter(location_name__in=location_names)

    if category_name:
        events_qs = events_qs.filter(category__name=category_name)
        
    if sort_by == 'recommendation':
        user_interests = user.interests.all()
        user_parent_category_names = {interest.parent_category.name for interest in user_interests}
        user_interest_keywords = set()
        for interest in user_interests:
            keywords = re.split(r'[,\s()]+', interest.name)
            user_interest_keywords.update([kw for kw in keywords if kw])

        events_list = list(events_qs)
        for event in events_list:
            bonus_score = 0
            if event.category and event.category.name in user_parent_category_names: bonus_score += 100
            if any(keyword in event.title for keyword in user_interest_keywords): bonus_score += 50
            event.final_score = event.recommendation_score + bonus_score
        
        events_list.sort(key=lambda x: (x.final_score, x.recommendation_score), reverse=True)
        return LocalEventSerializer(events_list, many=True).data
    else:
        events_qs = events_qs.order_by('-start_date')
        return LocalEventSerializer(events_qs, many=True).data

# ------------------------------------------------------------------------------------
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ Helper Functions (전문가 함수들) ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
# ------------------------------------------------------------------------------------


# API 1: 카테고리 선택 버튼 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def event_category_list_view(request):
    categories = Category.objects.all()
    formatted_categories = [{'type': 'category', 'name': cat.name} for cat in categories]
    response_data = formatted_categories + [{'type': 'recommendation', 'name': 'NestOn 추천 행사 보기'}]
    return Response(response_data)


# API 2: 지역 행사 목록 조회 (라우터 역할)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_list_view(request):
    user = request.user
    category_name = request.query_params.get('category')
    sort_by = request.query_params.get('sort')

    # '상권.쇼핑 이벤트'는 위치와 무관하게 별도 DB 조회 함수 호출
    if category_name == '상권.쇼핑 이벤트':
        results = _fetch_shopping_data(user)
        return Response(results)

    # 그 외 모든 카테고리는 위치 기반 DB 조회
    location_type = request.query_params.get('location_type')
    if not location_type or location_type not in ['my_location', 'interested']:
        return Response({"error": "location_type 파라미터가 필요합니다."}, status=400)

    locations_to_check = []
    if location_type == 'my_location':
        if not user.my_location: return Response({"error": "'내 지역'을 먼저 설정해주세요."}, status=400)
        locations_to_check.append(user.my_location)
    else: # 'interested'
        user_locations = user.interested_locations.all()
        if not user_locations.exists(): return Response([])
        locations_to_check.extend(user_locations)
    
    results = _fetch_db_events(locations_to_check, category_name, sort_by, user)
    return Response(results)


# API 3: 행사 상세 정보 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail_view(request, pk):
    try:
        event = LocalEvent.objects.get(pk=pk)
    except LocalEvent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = LocalEventDetailSerializer(event)
    return Response(serializer.data)