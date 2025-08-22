from rest_framework import serializers
from .models import PublicAlert

class PublicAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicAlert
        fields = ['id', 'title', 'content', 'category', 'published_at', 'location_name', 'source']