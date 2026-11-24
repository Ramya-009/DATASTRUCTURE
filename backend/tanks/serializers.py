from rest_framework import serializers
from .models import Tank

class TankSerializer(serializers.ModelSerializer):
    water_level_percentage = serializers.ReadOnlyField()
    available_water_litres = serializers.ReadOnlyField()

    class Meta:
        model = Tank
        fields = [
            'id', 'tank_id', 'tank_name', 'location',
            'capacity', 'current_level', 'water_level_percentage',
            'available_water_litres', 'status', 'updated_at', 'created_at'
        ]
