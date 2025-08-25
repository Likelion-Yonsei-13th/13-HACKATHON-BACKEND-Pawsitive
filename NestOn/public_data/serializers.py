from rest_framework import serializers
from .models import PublicAlert,CulturalFacility

class PublicAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicAlert
        fields = ['id',  'unique_id', 'title', 'content', 'category', 'published_at', 'location_name', 'source']

class CulturalFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CulturalFacility
        # 모델의 모든 필드를 그대로 보여주되, id 필드만 제외
        exclude = ['id']