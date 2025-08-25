from rest_framework import serializers
from .models import LocalEvent,CommercialArea

class LocalEventSerializer(serializers.ModelSerializer):
    # Foreign Key로 연결된 Category 모델의 'name' 필드를 가져옵니다.
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = LocalEvent
        # 프론트엔드에 전달할 필드 목록을 최신 모델에 맞게 업데이트합니다.
        fields = [
            'id', 
            'title', 
            'content', 
            'category_name', 
            'start_date', 
            'end_date', 
            'location_name', 
            'place',         # '장소' 필드 추가
            'image_url', 
            'org_link'       # '홈페이지 링크' 필드 추가
        ]

class LocalEventDetailSerializer(serializers.ModelSerializer):
    # Foreign Key로 연결된 Category 모델의 'name' 필드를 가져옵니다.
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = LocalEvent
        # '__all__'을 사용해 모델의 모든 필드를 포함시킵니다.
        fields = '__all__'

class CommercialAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommercialArea
        # 요청하신 5개 필드를 제외한 모든 필드를 포함합니다.
        exclude = [
            'area_sh_payment_amt_min',
            'area_sh_payment_amt_max',
            'rsb_sh_payment_amt_min',
            'rsb_sh_payment_amt_max',
            'cmrcl_corporation_rate'
        ]