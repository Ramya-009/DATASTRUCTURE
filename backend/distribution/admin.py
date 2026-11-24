from django.contrib import admin
from .models import DistributionSchedule

@admin.register(DistributionSchedule)
class DistributionScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'tank', 'scheduled_date', 'start_time', 'end_time', 'allocated_quantity', 'status')
    list_filter = ('scheduled_date', 'status', 'area', 'tank')
    search_fields = ('area__area_name', 'tank__tank_name')
