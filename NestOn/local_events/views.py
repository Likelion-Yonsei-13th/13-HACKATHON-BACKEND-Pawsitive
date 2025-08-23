from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from rest_framework import status 
from operator import itemgetter
import re # 키워드 추출을 위한 re 모듈 import
from User.models import Category # User 앱의 Category 모델을 가져옵니다.

# --- 테스트를 위한 실제와 유사한 임시 데이터 ---
MOCK_EVENTS = [
    {'id': 1, 'title': '서대문독립축제', 'content': '서대문형무소역사관에서 열리는 뜻깊은 축제', 'category': '축제.마켓', 'start_date': '2025-08-14', 'end_date': '2025-08-16', 'location_name': '서대문구', 'image_url': 'https://i.ibb.co/P9gHw0G/image.png', 'recommendation_score': 95},
    {'id': 2, 'title': '한강 재즈 페스티벌', 'content': '여의도 한강공원에서 즐기는 야외 재즈 공연', 'category': '문화.예술', 'start_date': '2025-09-05', 'end_date': '2025-09-06', 'location_name': '영등포구', 'image_url': '', 'recommendation_score': 90},
    {'id': 3, 'title': '강남 코딩 교육 세미나', 'content': '초보자를 위한 파이썬 무료 강연', 'category': '교육.강연', 'start_date': '2025-08-25', 'end_date': '2025-08-25', 'location_name': '강남구', 'image_url': '', 'recommendation_score': 85},
    {'id': 4, 'title': '강남역 푸드트럭 축제', 'content': '다양한 음식을 맛볼 수 있는 기회', 'category': '축제.마켓', 'start_date': '2025-08-23', 'end_date': '2025-08-24', 'location_name': '강남구', 'image_url': '', 'recommendation_score': 92},
    {'id': 5, 'title': '서울시민 마라톤 대회', 'content': '상암 월드컵경기장에서 출발하는 마라톤', 'category': '스포츠.레저', 'start_date': '2025-10-12', 'end_date': '2025-10-12', 'location_name': '마포구', 'image_url': '', 'recommendation_score': 88},
    {'id': 6, 'title': '서대문 안산 클린 하이킹', 'content': '등산하며 환경 정화 활동에 참여하세요', 'category': '사회.봉사', 'start_date': '2025-09-07', 'end_date': '2025-09-07', 'location_name': '서대문구', 'image_url': '', 'recommendation_score': 80},
    {'id': 7, 'title': '신상 브랜드 런칭 팝업스토어', 'content': '더현대 서울에서 열리는 팝업스토어', 'category': '상권.쇼핑 이벤트', 'start_date': '2025-08-29', 'end_date': '2025-09-10', 'location_name': '영등포구', 'image_url': '', 'recommendation_score': 75},
]
# ------------------------------------

# API 1: 카테고리 선택 버튼 목록 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def event_category_list_view(request):
    """
    프론트엔드가 '6개 카테고리 + 추천 행사 보기' 버튼 화면을 구성할 때 호출할 API입니다.
    """
    categories = Category.objects.all()
    # DB에서 가져온 6개 카테고리 정보
    formatted_categories = [{'type': 'category', 'name': cat.name} for cat in categories]
    
    # 'NestOn 추천 행사 보기' 버튼 정보를 백엔드에서 직접 추가
    response_data = formatted_categories + [{'type': 'recommendation', 'name': 'NestOn 추천 행사 보기'}]
    
    return Response(response_data)


# API 2: 지역 행사 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_list_view(request):
    user = request.user
    location_type = request.query_params.get('location_type')

    if not location_type or location_type not in ['my_location', 'interested']:
        return Response({"error": "location_type 파라미터(my_location 또는 interested)가 필요합니다."}, status=400)

    # 1. 지역 필터링 (기존과 동일)
    if location_type == 'my_location':
        if not user.my_location:
            return Response({"error": "'내 지역'을 먼저 설정해주세요."}, status=400)
        location_names = [user.my_location.level2_district]
    else: # 'interested'
        user_locations = user.interested_locations.all()
        if not user_locations.exists():
            return Response([])
        location_names = [loc.level2_district for loc in user_locations]

    events = [event for event in MOCK_EVENTS if event['location_name'] in location_names]
    
    # 2. 카테고리 필터링 (기존과 동일)
    category_name = request.query_params.get('category')
    if category_name:
        events = [event for event in events if event['category'] == category_name]
        
    # 3. 정렬 방식 결정
    sort_by = request.query_params.get('sort')
    if sort_by == 'recommendation':

        user_interests = user.interests.all()
        # 3-1. 사용자가 선택한 관심사의 '상위 카테고리' 목록을 미리 준비
        user_parent_category_names = {interest.parent_category.name for interest in user_interests}
        # 3-2. 사용자가 선택한 관심사의 '하위 카테고리' 이름에서 키워드 추출
        # 예: "지역공연(연극, 뮤지컬)" -> ["지역공연", "연극", "뮤지컬"]
        user_interest_keywords = set()
        for interest in user_interests:
            # 괄호와 콤마를 기준으로 단어들을 분리
            keywords = re.split(r'[,\s()]+', interest.name)
            user_interest_keywords.update([kw for kw in keywords if kw])

        for event in events:
            bonus_score = 0
            # 3-3. 1차 가산점: 상위 카테고리가 일치하면 +100점
            if event['category'] in user_parent_category_names:
                bonus_score += 100
            
            # 3-4. 2차 가산점: 행사 제목에 하위 카테고리 키워드가 있으면 +50점
            if any(keyword in event['title'] for keyword in user_interest_keywords):
                bonus_score += 50
            
            event['final_score'] = event.get('recommendation_score', 0) + bonus_score

        events.sort(key=itemgetter('final_score', 'recommendation_score'), reverse=True)
    else:
        # 기본은 최신순(시작 날짜 기준) 정렬
        events.sort(key=itemgetter('start_date'), reverse=True)
        
    return Response(events)