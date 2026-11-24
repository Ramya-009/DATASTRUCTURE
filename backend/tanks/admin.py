from django.contrib import admin
from .models import Tank

@admin.register(Tank)
class TankAdmin(admin.ModelAdmin):
    list_display = ('tank_id', 'tank_name', 'location', 'capacity', 'current_level', 'water_level_percentage', 'status', 'updated_at')
    list_filter = ('status', 'location')
    search_fields = ('tank_id', 'tank_name', 'location')
