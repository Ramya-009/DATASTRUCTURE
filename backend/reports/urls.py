from django.urls import path
from .views import AdminDashboardSummaryView, DemandPredictionView, DailyReportView

urlpatterns = [
    path('summary/', AdminDashboardSummaryView.as_view(), name='api-admin-summary'),
    path('demand-prediction/', DemandPredictionView.as_view(), name='api-demand-prediction'),
    path('daily/', DailyReportView.as_view(), name='api-daily-report'),
]
