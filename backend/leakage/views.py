from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeakageReport
from .serializers import LeakageReportSerializer
from water.c_bridge import c_bridge
from water.models import Area
from notifications.models import Notification
from users.models import CustomUser

class LeakageReportListView(APIView):
    def get(self, request):
        reports = LeakageReport.objects.all().order_by('-reported_date')
        status_param = request.query_params.get('status')
        if status_param:
            reports = reports.filter(status=status_param)
        area_id = request.query_params.get('area_id')
        if area_id:
            reports = reports.filter(area_id=area_id)

        serializer = LeakageReportSerializer(reports, many=True)
        return Response({
            'success': True,
            'count': reports.count(),
            'reports': serializer.data
        })

    def post(self, request):
        data = request.data.copy()
        if request.user.is_authenticated and 'user' not in data:
            data['user'] = request.user.id
            if request.user.area and 'area' not in data:
                data['area'] = request.user.area.id

        serializer = LeakageReportSerializer(data=data)
        if serializer.is_valid():
            leak = serializer.save()

            # Alert admin users of a new leakage report
            for admin_user in CustomUser.objects.filter(role='ADMIN'):
                Notification.objects.create(
                    user=admin_user,
                    title="NEW LEAK REPORTED",
                    message=f"Leak reported in {leak.area.area_name} at {leak.location}: {leak.description[:80]}...",
                    notification_type="EMERGENCY" if leak.severity in ('HIGH', 'CRITICAL') else "ALERT"
                )

            return Response({
                'success': True,
                'message': 'Leakage report lodged successfully. Our field maintenance team has been alerted.',
                'report': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LeakageReportDetailView(APIView):
    def put(self, request, pk):
        try:
            leak = LeakageReport.objects.get(pk=pk)
        except LeakageReport.DoesNotExist:
            return Response({'success': False, 'message': 'Leakage report not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        admin_comment = request.data.get('admin_comment')
        loss_vol = request.data.get('loss_volume_litres')

        if new_status:
            leak.status = new_status
            if new_status == 'RESOLVED':
                leak.resolved_at = timezone.now()
        if admin_comment is not None:
            leak.admin_comment = admin_comment
        if loss_vol is not None:
            leak.loss_volume_litres = float(loss_vol)

        leak.save()

        # If user who reported is known, notify them
        if leak.user:
            Notification.objects.create(
                user=leak.user,
                title="Leak Report Update",
                message=f"The reported leak at {leak.location} is now: {leak.status}.",
                notification_type="INFO"
            )

        return Response({
            'success': True,
            'message': f'Leak report #{pk} updated successfully.',
            'report': LeakageReportSerializer(leak).data
        })


class DetectAnomalyLeakageView(APIView):
    """
    Core Intelligent Module: Section 34
    Calculates differential between Tank Output and Area Received Quantity
    Calls C engine detect_leakage_anomaly
    """
    def post(self, request):
        tank_output = float(request.data.get('tank_output_litres', 10000.0))
        area_received = float(request.data.get('area_received_litres', 7800.0))
        threshold = float(request.data.get('threshold_percentage', 8.0))
        area_id = request.data.get('area_id')

        # Execute C Anomaly Algorithm
        analysis = c_bridge.detect_leakage(tank_output, area_received, threshold)

        # If high or critical leak anomaly detected and area specified, auto-log pipeline alert
        if analysis['is_leak_detected'] and area_id:
            try:
                area_obj = Area.objects.get(pk=area_id)
                LeakageReport.objects.create(
                    area=area_obj,
                    location=f"Main Feeder Pipeline to {area_obj.area_name}",
                    description=f"Automated Anomaly Alert from C Engine: Output was {tank_output}L but only {area_received}L registered. Unaccounted loss: {analysis['loss_litres']}L ({analysis['loss_percentage']}%).",
                    severity=analysis['severity'],
                    loss_volume_litres=analysis['loss_litres'],
                    status='REPORTED'
                )
            except Area.DoesNotExist:
                pass

        return Response({
            'success': True,
            'analysis': analysis
        })
