from django.contrib import admin
from .models import Area, WaterRequest, WaterUsage, Feedback

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_name', 'location', 'population', 'priority', 'daily_quota_litres', 'status')
    list_filter = ('priority', 'status')
    search_fields = ('area_name', 'location')

@admin.register(WaterRequest)
class WaterRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'area', 'requested_quantity', 'allocated_quantity', 'request_date', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'area', 'request_date')
    search_fields = ('user__name', 'user__email', 'reason')

@admin.register(WaterUsage)
class WaterUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'area', 'quantity', 'usage_date', 'source')
    list_filter = ('usage_date', 'area', 'source')
    search_fields = ('user__name', 'area__area_name')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
