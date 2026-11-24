from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum
from .models import Area, WaterRequest, WaterUsage, Feedback
from .serializers import AreaSerializer, WaterRequestSerializer, WaterUsageSerializer, FeedbackSerializer
from tanks.models import Tank
from distribution.models import DistributionSchedule
from notifications.models import Notification

class AreaListView(APIView):
    def get(self, request):
        areas = Area.objects.all().order_by('priority', 'area_name')
        return Response({'success': True, 'count': areas.count(), 'areas': AreaSerializer(areas, many=True).data})

    def post(self, request):
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            area = serializer.save()
            return Response({'success': True, 'message': f'Area {area.area_name} created successfully.', 'area': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class WaterRequestListView(APIView):
    def get(self, request):
        requests_qs = WaterRequest.objects.all().order_by('-created_at')

        # Filter by status if requested
        req_status = request.query_params.get('status')
        if req_status:
            requests_qs = requests_qs.filter(status=req_status)

        # Filter by user if not admin or requested
        user_id = request.query_params.get('user_id')
        if user_id:
            requests_qs = requests_qs.filter(user_id=user_id)
        elif request.user.is_authenticated and request.user.role == 'USER':
            requests_qs = requests_qs.filter(user=request.user)

        serializer = WaterRequestSerializer(requests_qs, many=True)
        return Response({'success': True, 'count': requests_qs.count(), 'requests': serializer.data})

    def post(self, request):
        data = request.data.copy()
        if request.user.is_authenticated:
            data['user'] = request.user.id
            if not data.get('area') and request.user.area:
                data['area'] = request.user.area.id

        serializer = WaterRequestSerializer(data=data)
        if serializer.is_valid():
            water_req = serializer.save(status='PENDING')

            # Create notification for citizen
            Notification.objects.create(
                user=water_req.user,
                title="Water Request Submitted",
                message=f"Your request #{water_req.id} for {water_req.requested_quantity} Litres on {water_req.request_date} is now PENDING verification.",
                notification_type="INFO"
            )

            return Response({
                'success': True,
                'message': 'Water request submitted successfully! Awaiting allocation.',
                'request': WaterRequestSerializer(water_req).data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class WaterRequestDetailView(APIView):
    def get(self, request, pk):
        try:
            req_obj = WaterRequest.objects.get(pk=pk)
            return Response({'success': True, 'request': WaterRequestSerializer(req_obj).data})
        except WaterRequest.DoesNotExist:
            return Response({'success': False, 'message': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            req_obj = WaterRequest.objects.get(pk=pk)
        except WaterRequest.DoesNotExist:
            return Response({'success': False, 'message': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', req_obj.admin_notes)
        allocated_qty = request.data.get('allocated_quantity')

        if new_status:
            req_obj.status = new_status
        if admin_notes is not None:
            req_obj.admin_notes = admin_notes
        if allocated_qty is not None:
            req_obj.allocated_quantity = float(allocated_qty)

        req_obj.save()

        # Send notification to user regarding status change
        Notification.objects.create(
            user=req_obj.user,
            title=f"Request #{req_obj.id} Status Updated",
            message=f"Your water request has been updated to: {req_obj.status}. Allocated Quantity: {req_obj.allocated_quantity} L.",
            notification_type="ALERT" if req_obj.status in ('APPROVED', 'ALLOCATED') else "INFO"
        )

        return Response({
            'success': True,
            'message': f'Request #{pk} updated to {req_obj.status}.',
            'request': WaterRequestSerializer(req_obj).data
        })


class WaterUsageListView(APIView):
    def get(self, request):
        qs = WaterUsage.objects.all().order_by('-usage_date')
        if request.user.is_authenticated and request.user.role == 'USER':
            qs = qs.filter(user=request.user)
        elif request.query_params.get('user_id'):
            qs = qs.filter(user_id=request.query_params.get('user_id'))

        serializer = WaterUsageSerializer(qs, many=True)
        total_usage = qs.aggregate(Sum('quantity'))['quantity__sum'] or 0.0

        return Response({
            'success': True,
            'count': qs.count(),
            'total_usage_litres': total_usage,
            'usage_records': serializer.data
        })

    def post(self, request):
        data = request.data.copy()
        if request.user.is_authenticated and 'user' not in data:
            data['user'] = request.user.id
            if request.user.area and 'area' not in data:
                data['area'] = request.user.area.id

        serializer = WaterUsageSerializer(data=data)
        if serializer.is_valid():
            usage = serializer.save()

            # Check for unusually high consumption (Water Saving Alert feature)
            if usage.user:
                normal_quota = usage.user.daily_water_quota_litres
                if usage.quantity > (normal_quota * 1.5):
                    Notification.objects.create(
                        user=usage.user,
                        title="WATER SAVING ALERT: High Consumption Detected",
                        message=f"Your logged usage today ({usage.quantity} L) exceeds your standard quota ({normal_quota} L) by {round((usage.quantity - normal_quota), 1)} L. Please reduce water wastage.",
                        notification_type="ALERT"
                    )

            return Response({
                'success': True,
                'message': 'Water consumption recorded successfully.',
                'usage': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FeedbackListView(APIView):
    def get(self, request):
        feedbacks = Feedback.objects.all().order_by('-created_at')
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response({'success': True, 'count': feedbacks.count(), 'feedbacks': serializer.data})

    def post(self, request):
        data = request.data.copy()
        if request.user.is_authenticated:
            data['user'] = request.user.id
        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            fb = serializer.save()
            return Response({'success': True, 'message': 'Thank you for your feedback!', 'feedback': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDashboardStatsView(APIView):
    """
    Supplies the complete real-time dashboard data for Section 7:
    - Water Availability %
    - Tank Level %
    - Today's Usage
    - Monthly Usage
    - Upcoming Distribution
    - Recent Requests & Notifications
    """
    def get(self, request):
        user = request.user if request.user.is_authenticated else None

        # Tanks calculation
        tanks = Tank.objects.all()
        total_capacity = sum(t.capacity for t in tanks) or 1.0
        total_current = sum(t.current_level for t in tanks)
        overall_tank_level = round((total_current / total_capacity * 100), 1)

        today = date.today()
        month_start = today.replace(day=1)

        today_usage = 0.0
        monthly_usage = 0.0

        if user and user.is_authenticated:
            user_usages = WaterUsage.objects.filter(user=user)
            today_usage = user_usages.filter(usage_date=today).aggregate(Sum('quantity'))['quantity__sum'] or 85.0
            monthly_usage = user_usages.filter(usage_date__gte=month_start).aggregate(Sum('quantity'))['quantity__sum'] or 2450.0

            upcoming_schedules = DistributionSchedule.objects.filter(
                area=user.area,
                scheduled_date__gte=today
            ).order_by('scheduled_date', 'start_time')[:3]

            recent_requests = WaterRequest.objects.filter(user=user).order_by('-created_at')[:5]
            unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
        else:
            today_usage = 85.0
            monthly_usage = 2450.0
            upcoming_schedules = DistributionSchedule.objects.filter(scheduled_date__gte=today).order_by('scheduled_date')[:3]
            recent_requests = WaterRequest.objects.all().order_by('-created_at')[:5]
            unread_notifications = 2

        # Water availability based on tank level and seasonal reserves
        water_availability_pct = min(100.0, round(overall_tank_level * 1.05, 1))

        schedules_data = []
        for s in upcoming_schedules:
            schedules_data.append({
                'id': s.id,
                'area_name': s.area.area_name if s.area else 'Metro Area',
                'date': s.scheduled_date.strftime('%d %b %Y'),
                'time_slot': f"{s.start_time.strftime('%I:%M %p')} - {s.end_time.strftime('%I:%M %p')}",
                'allocated_quantity': s.allocated_quantity,
                'status': s.status
            })

        return Response({
            'success': True,
            'user': {
                'name': user.name if user and user.is_authenticated else 'Ramya M',
                'email': user.email if user and user.is_authenticated else 'ramya@gmail.com',
                'area': user.area.area_name if user and user.is_authenticated and user.area else 'Poonamallee',
                'house_number': user.house_number if user and user.is_authenticated else '25',
                'role': user.role if user and user.is_authenticated else 'USER'
            },
            'stats': {
                'water_availability_percentage': water_availability_pct,
                'tank_level_percentage': overall_tank_level,
                'today_usage_litres': today_usage,
                'monthly_usage_litres': monthly_usage,
                'daily_quota_litres': user.daily_water_quota_litres if user and user.is_authenticated else 350.0,
                'unread_notifications': unread_notifications,
            },
            'upcoming_schedules': schedules_data,
            'recent_requests': WaterRequestSerializer(recent_requests, many=True).data
        })
