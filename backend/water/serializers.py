from rest_framework import serializers
from .models import Area, WaterRequest, WaterUsage, Feedback

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'area_name', 'location', 'population', 'priority', 'daily_quota_litres', 'status', 'created_at']


class WaterRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    area_name = serializers.CharField(source='area.area_name', read_only=True)

    class Meta:
        model = WaterRequest
        fields = [
            'id', 'user', 'user_name', 'user_email', 'area', 'area_name',
            'requested_quantity', 'allocated_quantity', 'request_date',
            'priority', 'reason', 'status', 'admin_notes', 'created_at'
        ]
        read_only_fields = ['allocated_quantity', 'created_at']


class WaterUsageSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    area_name = serializers.CharField(source='area.area_name', read_only=True)

    class Meta:
        model = WaterUsage
        fields = ['id', 'user', 'user_name', 'area', 'area_name', 'quantity', 'usage_date', 'source', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'rating', 'comments', 'created_at']
