# User/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

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

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            return user
        raise serializers.ValidationError("아이디 또는 비밀번호가 올바르지 않습니다.")