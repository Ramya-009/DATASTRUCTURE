from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from users.models import CustomUser

class NotificationListView(APIView):
    def get(self, request):
        qs = Notification.objects.all().order_by('-created_at')
        if request.user.is_authenticated and request.user.role == 'USER':
            qs = qs.filter(user=request.user)
        elif request.query_params.get('user_id'):
            qs = qs.filter(user_id=request.query_params.get('user_id'))

        unread_only = request.query_params.get('unread')
        if unread_only in ('true', '1'):
            qs = qs.filter(is_read=False)

        serializer = NotificationSerializer(qs, many=True)
        return Response({
            'success': True,
            'count': qs.count(),
            'unread_count': qs.filter(is_read=False).count(),
            'notifications': serializer.data
        })

    def post(self, request):
        # Admin sending a broadcast or direct alert
        target_role = request.data.get('target_role')
        target_area = request.data.get('target_area')
        title = request.data.get('title', 'System Announcement')
        message = request.data.get('message', '')
        notif_type = request.data.get('notification_type', 'INFO')

        users = CustomUser.objects.all()
        if target_role:
            users = users.filter(role=target_role)
        if target_area:
            users = users.filter(area_id=target_area)

        created_count = 0
        for u in users:
            Notification.objects.create(
                user=u,
                title=title,
                message=message,
                notification_type=notif_type
            )
            created_count += 1

        return Response({
            'success': True,
            'message': f"Broadcast delivered to {created_count} users successfully.",
            'recipient_count': created_count
        }, status=status.HTTP_201_CREATED)


class MarkNotificationReadView(APIView):
    def put(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk)
            n.is_read = True
            n.save()
            return Response({'success': True, 'message': 'Notification marked as read.'})
        except Notification.DoesNotExist:
            return Response({'success': False, 'message': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)


class MarkAllNotificationsReadView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        else:
            Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({'success': True, 'message': 'All notifications marked as read.'})
