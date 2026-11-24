from django.contrib import admin
from .models import LeakageReport

@admin.register(LeakageReport)
class LeakageReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'location', 'severity', 'loss_volume_litres', 'status', 'reported_date', 'resolved_at')
    list_filter = ('severity', 'status', 'area')
    search_fields = ('location', 'description', 'area__area_name')
