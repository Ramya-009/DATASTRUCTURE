from rest_framework import serializers
from .models import LeakageReport

class LeakageReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='user.name', read_only=True, default='Anonymous')
    reporter_mobile = serializers.CharField(source='user.mobile', read_only=True, default='')
    area_name = serializers.CharField(source='area.area_name', read_only=True)

    class Meta:
        model = LeakageReport
        fields = [
            'id', 'user', 'reporter_name', 'reporter_mobile', 'area', 'area_name',
            'location', 'description', 'reported_date', 'severity',
            'loss_volume_litres', 'status', 'admin_comment', 'resolved_at'
        ]
