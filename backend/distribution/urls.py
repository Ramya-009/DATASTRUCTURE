from django.urls import path
from .views import DistributionScheduleListView, DistributionScheduleDetailView, RunDistributionAlgorithmView

urlpatterns = [
    path('schedules/', DistributionScheduleListView.as_view(), name='api-schedules-list'),
    path('schedules/<int:pk>/', DistributionScheduleDetailView.as_view(), name='api-schedule-detail'),
    path('run-algorithm/', RunDistributionAlgorithmView.as_view(), name='api-run-distribution-algorithm'),
]
