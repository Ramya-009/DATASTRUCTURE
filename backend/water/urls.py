from django.urls import path
from .views import (
    AreaListView,
    WaterRequestListView,
    WaterRequestDetailView,
    WaterUsageListView,
    FeedbackListView,
    UserDashboardStatsView
)

urlpatterns = [
    path('areas/', AreaListView.as_view(), name='api-areas-list'),
    path('requests/', WaterRequestListView.as_view(), name='api-requests-list'),
    path('requests/<int:pk>/', WaterRequestDetailView.as_view(), name='api-request-detail'),
    path('usage/', WaterUsageListView.as_view(), name='api-usage-list'),
    path('feedback/', FeedbackListView.as_view(), name='api-feedback-list'),
    path('dashboard/stats/', UserDashboardStatsView.as_view(), name='api-dashboard-stats'),
]
