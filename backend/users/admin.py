from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('name', 'email', 'mobile', 'role', 'area', 'house_number', 'status', 'is_staff')
    list_filter = ('role', 'status', 'area')
    search_fields = ('name', 'email', 'mobile', 'house_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Water Distribution Info', {
            'fields': ('name', 'mobile', 'address', 'area', 'house_number', 'role', 'daily_water_quota_litres', 'status')
        }),
    )
