from rest_framework import serializers
from .models import DistributionSchedule

class DistributionScheduleSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.area_name', read_only=True)
    tank_name = serializers.CharField(source='tank.tank_name', read_only=True)
    tank_id_code = serializers.CharField(source='tank.tank_id', read_only=True)

    class Meta:
        model = DistributionSchedule
        fields = [
            'id', 'area', 'area_name', 'tank', 'tank_name', 'tank_id_code',
            'scheduled_date', 'start_time', 'end_time', 'allocated_quantity',
            'status', 'created_at'
        ]
