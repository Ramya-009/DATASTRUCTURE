from django.urls import path
from .views import LeakageReportListView, LeakageReportDetailView, DetectAnomalyLeakageView

urlpatterns = [
    path('reports/', LeakageReportListView.as_view(), name='api-leakage-reports-list'),
    path('reports/<int:pk>/', LeakageReportDetailView.as_view(), name='api-leakage-report-detail'),
    path('detect-anomaly/', DetectAnomalyLeakageView.as_view(), name='api-detect-leakage-anomaly'),
]
