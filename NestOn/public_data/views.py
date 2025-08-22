from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import PublicAlert

# --- 테스트용 가짜 데이터 ---
MOCK_DATA = {
    "disaster": [
        {"id": 1, "title": "[기상청] 서울 전역 호우주의보 발령", "content": "22일 오후 2시를 기해 서울 전역에 호우주의보가 발령되었습니다...", "category": "disaster", "published_at": "2025-08-22T14:05:00Z", "location_name": "서울특별시", "source": "기상청"},
    ],
    "accident": [
        {"id": 2, "title": "[강남소방서] 삼성역 인근 도로 3중 추돌사고 발생", "content": "삼성역 사거리에서 3중 추돌사고가 발생하여 주변 도로가 혼잡합니다...", "category": "accident", "published_at": "2025-08-22T14:15:00Z", "location_name": "강남구", "source": "강남소방서"},
    ],
    "traffic": [
        {"id": 3, "title": "[교통정보] 올림픽대로 잠실 방향 정체", "content": "올림픽대로 잠실 방향, 한남대교 남단부터 차량 정체가 이어지고 있습니다...", "category": "traffic", "published_at": "2025-08-22T14:25:00Z", "location_name": "서울특별시", "source": "서울교통정보센터"},
    ],
    "safety": [
        {"id": 4, "title": "[경찰청] 보이스피싱 주의 안내", "content": "최근 검찰, 경찰을 사칭한 보이스피싱 사례가 증가하고 있습니다...", "category": "safety", "published_at": "2025-08-22T10:10:00Z", "location_name": "서울특별시", "source": "경찰청"},
    ],
    "facility": [
        {"id": 5, "title": "[마포구청] 상수도관 파열로 인한 단수 안내", "content": "성산동 일대 상수도관 파열로 복구 작업 중이며, 일부 지역에 단수가 예상됩니다.", "category": "facility", "published_at": "2025-08-22T14:00:00Z", "location_name": "마포구", "source": "마포구청"},
    ],
    "etc": [
        {"id": 6, "title": "[서울시] '책읽는 서울광장' 주말 행사 안내", "content": "이번 주말, 서울광장에서 다채로운 북콘서트와 문화행사가 열립니다...", "category": "etc", "published_at": "2025-08-22T11:00:00Z", "location_name": "중구", "source": "서울시"},
    ]
}

# API 1: 카테고리 선택 화면을 위한 API
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    categories = PublicAlert.ALERT_CATEGORIES
    formatted_categories = [{'key': key, 'name': name} for key, name in categories]
    return Response(formatted_categories)

# API 2: 상세 목록 화면을 위한 API
@api_view(['GET'])
@permission_classes([AllowAny])
def alert_list_view(request, category_key):
    if category_key not in MOCK_DATA:
        return Response({"error": "존재하지 않는 카테고리입니다."}, status=status.HTTP_404_NOT_FOUND)

    data = MOCK_DATA.get(category_key)
    return Response(data)