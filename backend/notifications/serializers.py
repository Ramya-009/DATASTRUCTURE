from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_name', 'title', 'message', 'notification_type', 'is_read', 'created_at']
