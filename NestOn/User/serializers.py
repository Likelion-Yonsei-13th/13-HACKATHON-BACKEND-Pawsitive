from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Location, Category, SubCategory

# AUTH_USER_MODEL 설정에 따라 현재 활성화된 User 모델을 가져옴
User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'password2', 'name', 'phone_number', 
            'birth_date', 'location_services_agreed', 'marketing_push_agreed',
            'terms_agreed', 'privacy_agreed'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        
        # 필수 약관 동의 여부 확인
        if not data.get('location_services_agreed'):
            raise serializers.ValidationError({"agreements": "위치 기반 서비스 약관(필수)에 동의해야 합니다."})
        if not data.get('terms_agreed'):
            raise serializers.ValidationError({"agreements": "이용약관(필수)에 동의해야 합니다."})
        if not data.get('privacy_agreed'):
            raise serializers.ValidationError({"agreements": "개인정보 취급방침(필수)에 동의해야 합니다."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
class SubCategorySerializer(serializers.ModelSerializer):
    # 부모 카테고리의 이름을 함께 보내기 위한 필드 추가
    parent_category_name = serializers.CharField(source='parent_category.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'parent_category_name'] # 필드 목록에 추가

class CategorySerializer(serializers.ModelSerializer):
    # 하위 카테고리 목록을 중첩해서 보여줌
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")
    
# 1. Location 모델을 위한 Serializer 추가
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'level1_city', 'level2_district', 'level3_borough']


# 2. 사용자 프로필 조회 및 수정을 위한 Serializer 추가
class UserProfileSerializer(serializers.ModelSerializer):
    my_location = LocationSerializer(read_only=True)
    interested_locations = LocationSerializer(many=True, read_only=True)
    interests = SubCategorySerializer(many=True, read_only=True) # 이제 SubCategory를 보여줌
    
    # 수정할 때는 ID 값만 받음 
    my_location_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    interested_location_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    # 사용자가 선택한 하위 카테고리 ID 목록을 받기 위한 필드
    interest_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'name',
            'my_location', 'interested_locations',         # 읽기용 필드
            'my_location_id', 'interested_location_ids'   # 쓰기용 필드
        ]

    def update(self, instance, validated_data):
        my_location_id = validated_data.get('my_location_id')
        if my_location_id is not None:
            # allow_null=True를 처리하기 위해, id가 0이면 None으로 간주
            instance.my_location_id = my_location_id if my_location_id else None

        interested_location_ids = validated_data.get('interested_location_ids')
        if interested_location_ids is not None:
            instance.interested_locations.set(interested_location_ids)

        # 관심사(하위 카테고리) 수정 로직 추가
        interest_ids = validated_data.get('interest_ids')
        if interest_ids is not None:
            instance.interests.set(interest_ids)

        instance.save()
        return instance