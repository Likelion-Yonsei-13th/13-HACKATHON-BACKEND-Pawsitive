from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import random

# from .serializers import ... 처럼 상대경로를 사용하므로 앱 이름 변경과 무관
from .serializers import UserSignupSerializer, UserLoginSerializer

from rest_framework.permissions import IsAuthenticated # 인증된 사용자만 접근 허용
from .models import Location
from .serializers import LocationSerializer, UserProfileSerializer

User = get_user_model()

VERIFICATION_CODES = {} # 실제로는 Redis 사용 추천

@api_view(['POST'])
@permission_classes([AllowAny])
def check_username_view(request):
    username = request.data.get('username')
    if not username:
        return Response({
            "status": 400,
            "success": False,
            "message": "아이디를 입력해주세요.",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    is_available = not User.objects.filter(username=username).exists()
    
    if is_available:
        # 사용 가능한 경우
        return Response({
            "status": 200,
            "success": True,
            "message": "사용 가능한 아이디입니다.",
            "data": {
                "is_available": True
            }
        })
    else:
        # 중복된 경우
        return Response({
            "status": 200,
            "success": False,
            "message": "중복된 아이디입니다. 다시 입력해주세요.",
            "data": {
                "is_available": False
            }
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_view(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': '휴대폰 번호를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    auth_code = str(random.randint(100000, 999999))
    VERIFICATION_CODES[phone_number] = auth_code
    print(f"To: {phone_number}, Code: {auth_code}") # 테스트용 콘솔 출력(Test용)
    return Response({'message': '인증번호가 발송되었습니다.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_sms_view(request):
    phone_number = request.data.get('phone_number')
    auth_code = request.data.get('auth_code')
    stored_code = VERIFICATION_CODES.get(phone_number)
    if stored_code and stored_code == auth_code:
        del VERIFICATION_CODES[phone_number]
        return Response({'message': '인증에 성공했습니다.'}, status=status.HTTP_200_OK)
    return Response({'error': '인증번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        return Response({'message': f"{user.username}님, 회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 1. 시/도 목록 API
@api_view(['GET'])
def city_list_view(request):
    cities = Location.objects.values_list('level1_city', flat=True).distinct()
    return Response(list(cities))

# 2. 시/군/구 목록 API
@api_view(['GET'])
def district_list_view(request):
    city = request.query_params.get('city')
    if not city:
        return Response({"error": "city 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    districts = Location.objects.filter(level1_city=city).values_list('level2_district', flat=True).distinct()
    return Response(list(districts))

# 3. 일반구 목록 API
@api_view(['GET'])
def borough_list_view(request):
    city = request.query_params.get('city')
    district = request.query_params.get('district')

    if not city or not district:
        return Response({"error": "city와 district 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    boroughs = Location.objects.filter(
        level1_city=city, 
        level2_district=district
    ).exclude(level3_borough__isnull=True).values_list('level3_borough', flat=True).distinct()
    
    return Response(list(boroughs))
    
# 4. 전체 Location 객체를 반환하는 API (ID 선택을 위해)
@api_view(['GET'])
def location_search_view(request):
    """
    프론트엔드에서 최종 선택된 지역의 ID를 찾기 위한 API.
    예: /api/user/locations/search/?city=경기도&district=성남시&borough=분당구
    """
    city = request.query_params.get('city')
    district = request.query_params.get('district')
    borough = request.query_params.get('borough', None)

    if not city or not district:
        return Response({"error": "city와 district가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if borough:
            location = Location.objects.get(level1_city=city, level2_district=district, level3_borough=borough)
        else:
            location = Location.objects.get(level1_city=city, level2_district=district, level3_borough__isnull=True)
        
        serializer = LocationSerializer(location)
        return Response(serializer.data)
    except Location.DoesNotExist:
        return Response({"error": "해당 지역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 5. 사용자 프로필 조회 및 수정 API
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
rom rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import random

# AWS 연동을 위해 추가된 라이브러리
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

from .serializers import UserSignupSerializer, UserLoginSerializer

User = get_user_model()

VERIFICATION_CODES = {}

@api_view(['POST'])
@permission_classes([AllowAny])
def check_username_view(request):
    username = request.data.get('username')
    if not username:
        return Response({'error': '아이디를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    is_available = not User.objects.filter(username=username).exists()
    return Response({'is_available': is_available})


# 실제 SMS 발송 로직으로 수정된 함수
@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_view(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': '휴대폰 번호를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 국가 코드가 없다면 추가 (한국 기준 +82)
    if not phone_number.startswith('+'):
        phone_number = f"+82{phone_number.lstrip('0')}"

    auth_code = str(random.randint(100000, 999999))
    VERIFICATION_CODES[phone_number] = auth_code
    
    # --- 실제 SMS 발송 로직 ---
    try:
        # settings.py에서 AWS 키를 가져와 boto3 클라이언트 생성
        client = boto3.client(
            "sns",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # 메시지 발송
        client.publish(
            PhoneNumber=phone_number,
            Message=f"[NestOn] 인증번호: {auth_code}"
        )
    except ClientError as e:
        # AWS 에러 처리
        print(f"AWS SNS Error: {e.response['Error']['Message']}")
        return Response({'error': '인증번호 발송에 실패했습니다. 잠시 후 다시 시도해주세요.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # 기타 에러 처리
        print(f"An unexpected error occurred: {e}")
        return Response({'error': '알 수 없는 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # -------------------------

    # print() 문은 이제 테스트용이므로 삭제하거나 주석 처리해도 됩니다.
    print(f"To: {phone_number}, Code: {auth_code}") 

    return Response({'message': '인증번호가 발송되었습니다.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_sms_view(request):
    phone_number = request.data.get('phone_number')
    auth_code = request.data.get('auth_code')
    
    # 인증번호 발송 시와 동일한 형식으로 번호 변경
    if not phone_number.startswith('+'):
        phone_number = f"+82{phone_number.lstrip('0')}"

    stored_code = VERIFICATION_CODES.get(phone_number)
    if stored_code and stored_code == auth_code:
        del VERIFICATION_CODES[phone_number]
        return Response({'message': '인증에 성공했습니다.'}, status=status.HTTP_200_OK)
    return Response({'error': '인증번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        return Response({'message': f"{user.username}님, 회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""