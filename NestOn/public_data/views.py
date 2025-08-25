import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import PublicAlert, GuardianHouse, CulturalFacility
from .serializers import PublicAlertSerializer, CulturalFacilitySerializer

#  카테고리별 '전문가' 함수들 
def _fetch_disaster_data(locations):
    """ '자연재해' 데이터를 처리하는 전문가 함수 (현재는 DB 조회) """
    # 향후 실시간 재난 API로 교체될 수 있는 부분입니다.
    # 현재는 DB에 저장된 재난문자를 조회합니다.
    if not locations:
        return []

    query = Q()
    for loc in locations:
        query |= Q(location_name__icontains=loc.level2_district)
    
    alerts = PublicAlert.objects.filter(category='disaster').filter(query)
    serializer = PublicAlertSerializer(alerts, many=True)
    return serializer.data

def _fetch_traffic_accident_data(locations, category):
    """ '교통' 및 '사고' 데이터를 처리하는 전문가 함수 """
    API_URL = "https://openapi.its.go.kr:9443/eventInfo"
    api_key = "ea6b45061ab2443fa58abd4c7dad5fed"
    all_raw_results = []

    for location in locations:
        if not (location and location.latitude and location.longitude): continue
        
        center_x, center_y = location.longitude, location.latitude
        coord_range = 0.1
        params = {
            "apiKey": api_key, "getType": "json",
            "minX": center_x - coord_range, "maxX": center_x + coord_range,
            "minY": center_y - coord_range, "maxY": center_y + coord_range,
            "type": "all", "eventType": "all",
        }
        try:
            response = requests.get(API_URL, params=params)
            items = response.json().get('body', {}).get('items', [])
            all_raw_results.extend(items)
        except requests.exceptions.RequestException:
            continue
    
    if category == 'accident':
        allowed_event_types = ['교통사고', '재난']
        all_raw_results = [item for item in all_raw_results if item.get('eventType') in allowed_event_types]

    # 표준 형식으로 변환
    standardized_results = []
    for item in all_raw_results:
        standardized_item = {
            "id": item.get("linkId"), "unique_id": item.get("linkId"),
            "title": f"[{item.get('eventType')}] {item.get('roadName', '위치 정보 없음')}",
            "content": item.get("message"), "category": category,
            "published_at": item.get("startDate"), "location_name": item.get("roadName"),
            "source": "도로교통공사"
        }
        standardized_results.append(standardized_item)
    
    return standardized_results

def _fetch_safety_data(locations):
    #'치안' 데이터를 DB에서 조회하고 사용자의 자치구로 필터링하는 함수
    if not locations:
        return []

    # 사용자의 '내 지역' 및 '관심 지역'의 자치구 이름 목록을 추출합니다.
    # 예: ['강남구', '종로구']
    gu_names = {loc.level2_district for loc in locations if loc.level2_district.endswith('구')}

    if not gu_names:
        return []

    # 해당 자치구에 속하는 안심지킴이집을 DB에서 조회합니다.
    nearby_houses = GuardianHouse.objects.filter(gu_name__in=list(gu_names))
    
    # 표준 형식으로 변환
    standardized_results = []
    for item in nearby_houses:
        standardized_item = {
            "id": item.id,
            "unique_id": item.id,
            "title": f"[{item.brand_name}] {item.store_name}",
            "content": item.address,
            "category": "safety",
            "published_at": None,
            "location_name": f"{item.gu_name} {item.store_name}",
            "source": "서울시 여성안심지킴이집"
        }
        standardized_results.append(standardized_item)
        
    return standardized_results
    
    # 표준 형식으로 변환
    standardized_results = []
    for item in nearby_facilities:
        standardized_item = {
            "id": item.id,
            "unique_id": item.id,
            "title": f"[{item.facility_type}] {item.name}",
            "content": f"주소: {item.address}, 전화번호: {item.tel}",
            "category": "safety",
            "published_at": None,
            "location_name": item.name,
            "source": item.police_office
        }
        standardized_results.append(standardized_item)
        
    return standardized_results

def _fetch_facility_data(locations):
    #'시설' 데이터를 DB에서 조회하고 새 Serializer로 변환하는 함수
    if not locations:
        return []

    location_keywords = {f"{loc.level1_city} {loc.level2_district}" for loc in locations}
    query = Q()
    for keyword in location_keywords:
        query |= Q(address__icontains=keyword)

    nearby_facilities = CulturalFacility.objects.filter(query)
    
    # 수동으로 데이터를 만드는 대신, 새로 만든 Serializer를 사용합니다.
    serializer = CulturalFacilitySerializer(nearby_facilities, many=True)
    return serializer.data


def _fetch_etc_data(locations):
    """ (미래) '기타' 데이터를 처리할 전문가 함수 """
    # TODO: 여기에 '기타' 관련 API 연동 코드 구현
    return []


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    categories = PublicAlert.ALERT_CATEGORIES
    formatted_categories = [{'key': key, 'name': name} for key, name in categories]
    return Response(formatted_categories)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_list_view(request):
    """ 요청을 받고 적절한 전문가에게 넘겨주는 '교통 경찰' 함수 """
    category = request.query_params.get('category')
    location_type = request.query_params.get('location_type')

    if not all([category, location_type]):
        return Response({"error": "category와 location_type 파라미터가 모두 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
    if location_type not in ['my_location', 'interested']:
        return Response({"error": "지역을 먼저 설정해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. 공통 로직: 사용자의 '내 지역' 또는 '관심 지역' 목록 준비
    locations_to_check = []
    if location_type == 'my_location':
        if request.user.my_location:
            locations_to_check.append(request.user.my_location)
    elif location_type == 'interested':
        locations_to_check.extend(request.user.interested_locations.all())

    if not locations_to_check:
        return Response([])

    # 2. Router: 카테고리에 맞는 전문가 함수 호출
    results = []
    if category == 'traffic' or category == 'accident':
        results = _fetch_traffic_accident_data(locations_to_check, category)
    elif category == 'disaster':
        results = _fetch_disaster_data(locations_to_check)
    elif category == 'safety':
        results = _fetch_safety_data(locations_to_check)
    elif category == 'facility':
        results = _fetch_facility_data(locations_to_check)
    elif category == 'etc':
        results = _fetch_etc_data(locations_to_check)

    return Response(results)