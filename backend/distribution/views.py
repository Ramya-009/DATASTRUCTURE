from datetime import date, datetime, time, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DistributionSchedule
from .serializers import DistributionScheduleSerializer
from water.models import WaterRequest, Area
from tanks.models import Tank
from notifications.models import Notification
from water.c_bridge import c_bridge

class DistributionScheduleListView(APIView):
    def get(self, request):
        schedules = DistributionSchedule.objects.all().order_by('-scheduled_date', 'start_time')
        area_id = request.query_params.get('area_id')
        if area_id:
            schedules = schedules.filter(area_id=area_id)

        serializer = DistributionScheduleSerializer(schedules, many=True)
        return Response({
            'success': True,
            'count': schedules.count(),
            'schedules': serializer.data
        })

    def post(self, request):
        serializer = DistributionScheduleSerializer(data=request.data)
        if serializer.is_valid():
            sched = serializer.save()

            # Notify residents in this area
            for resident in sched.area.residents.all():
                Notification.objects.create(
                    user=resident,
                    title="Water Distribution Scheduled",
                    message=f"Water distribution scheduled for your area ({sched.area.area_name}) on {sched.scheduled_date.strftime('%d %b %Y')} from {sched.start_time.strftime('%I:%M %p')} to {sched.end_time.strftime('%I:%M %p')}. Volume: {sched.allocated_quantity} L.",
                    notification_type="SCHEDULE"
                )

            return Response({
                'success': True,
                'message': 'Distribution schedule created and citizens notified successfully.',
                'schedule': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DistributionScheduleDetailView(APIView):
    def put(self, request, pk):
        try:
            sched = DistributionSchedule.objects.get(pk=pk)
        except DistributionSchedule.DoesNotExist:
            return Response({'success': False, 'message': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status:
            sched.status = new_status
            sched.save()
            return Response({'success': True, 'message': f'Schedule status updated to {new_status}.', 'schedule': DistributionScheduleSerializer(sched).data})
        return Response({'success': False, 'message': 'Status parameter missing.'}, status=status.HTTP_400_BAD_REQUEST)


class RunDistributionAlgorithmView(APIView):
    """
    Executes the C-based Priority Queue & Graph flow algorithm
    Integrates Section 14, 15, 16 & 33 end-to-end.
    """
    def post(self, request):
        # 1. Determine available water
        tanks = Tank.objects.filter(status='ACTIVE')
        total_tank_water = sum(t.current_level for t in tanks)

        override_water = request.data.get('available_water')
        if override_water is not None:
            try:
                available_water = float(override_water)
            except ValueError:
                available_water = total_tank_water
        else:
            available_water = total_tank_water

        # 2. Gather pending requests (or all requests for today/tomorrow)
        pending_requests_qs = WaterRequest.objects.filter(status__in=['PENDING', 'APPROVED']).order_by('priority', 'created_at')

        if not pending_requests_qs.exists():
            return Response({
                'success': False,
                'message': 'No pending water requests found to allocate. All requests are already processed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Format requests for C engine
        requests_payload = []
        for r in pending_requests_qs:
            requests_payload.append({
                'id': r.id,
                'user_id': r.user.id,
                'area_id': r.area.id,
                'priority': r.priority,
                'requested_quantity': r.requested_quantity,
                'reason': r.reason
            })

        # 4. EXECUTE C ALGORITHM ENGINE (Priority Queue Min-Heap + Graph Flow)
        algorithm_output = c_bridge.allocate_water(available_water, requests_payload)

        # 5. Apply results to Database
        results = algorithm_output.get('results', [])
        summary = algorithm_output.get('summary', {})

        allocated_by_area = {}

        for res in results:
            req_id = res['request_id']
            alloc_qty = res['allocated_quantity']
            res_status = res['status']

            try:
                db_req = WaterRequest.objects.get(id=req_id)
                db_req.allocated_quantity = alloc_qty
                db_req.status = 'ALLOCATED' if alloc_qty > 0 else 'REJECTED'
                db_req.admin_notes = f"Processed by C Priority Queue. {alloc_qty}L allocated (Satisfaction: {res['satisfaction_rate']}%)."
                db_req.save()

                if alloc_qty > 0:
                    area_id = db_req.area.id
                    allocated_by_area[area_id] = allocated_by_area.get(area_id, 0.0) + alloc_qty

                # Send Notification to User
                if alloc_qty > 0:
                    msg = f"Water Allocation Update: {alloc_qty} Litres allocated for your request #{db_req.id} (Satisfaction: {res['satisfaction_rate']}%). Distribution is being scheduled."
                else:
                    msg = f"Water Allocation Update: Your request #{db_req.id} could not be allocated due to water availability constraints and priority quota."

                Notification.objects.create(
                    user=db_req.user,
                    title="Water Allocation Decision",
                    message=msg,
                    notification_type="ALERT" if alloc_qty > 0 else "INFO"
                )
            except WaterRequest.DoesNotExist:
                continue

        # 6. Auto-generate Distribution Schedules per Area for tomorrow
        target_date = date.today() + timedelta(days=1)
        default_tank = tanks.first()

        schedules_created = []
        time_slots = [
            (time(6, 0), time(8, 0)),
            (time(8, 0), time(10, 0)),
            (time(16, 0), time(18, 0)),
            (time(18, 0), time(20, 0))
        ]

        slot_idx = 0
        for area_id, area_vol in allocated_by_area.items():
            if area_vol > 0 and default_tank:
                slot = time_slots[slot_idx % len(time_slots)]
                slot_idx += 1

                area_obj = Area.objects.get(id=area_id)
                sched = DistributionSchedule.objects.create(
                    area=area_obj,
                    tank=default_tank,
                    scheduled_date=target_date,
                    start_time=slot[0],
                    end_time=slot[1],
                    allocated_quantity=round(area_vol, 1),
                    status='SCHEDULED'
                )
                schedules_created.append(DistributionScheduleSerializer(sched).data)

        # 7. Deduct allocated water from Tank current level
        total_allocated = summary.get('total_allocated_water', 0.0)
        if default_tank and total_allocated > 0:
            default_tank.current_level = max(0.0, default_tank.current_level - total_allocated)
            default_tank.save()

        return Response({
            'success': True,
            'message': f"Distribution algorithm completed successfully via {algorithm_output.get('engine')}!",
            'engine_used': algorithm_output.get('engine'),
            'summary': summary,
            'results': results,
            'schedules_created': schedules_created
        })
