from django.urls import path
from .views import TankListCreateView, TankDetailView

urlpatterns = [
    path('', TankListCreateView.as_view(), name='api-tank-list-create'),
    path('<int:pk>/', TankDetailView.as_view(), name='api-tank-detail'),
]
