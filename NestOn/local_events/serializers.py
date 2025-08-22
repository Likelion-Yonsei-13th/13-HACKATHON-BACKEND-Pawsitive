from rest_framework import serializers
from .models import LocalEvent

class LocalEventSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = LocalEvent
        fields = [
            'id', 'title', 'content', 'category_name', 
            'start_date', 'end_date', 'location_name', 'image_url'
        ]