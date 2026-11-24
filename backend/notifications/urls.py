from django.urls import path
from .views import NotificationListView, MarkNotificationReadView, MarkAllNotificationsReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='api-notifications-list'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='api-notification-read'),
    path('read-all/', MarkAllNotificationsReadView.as_view(), name='api-notifications-read-all'),
]
