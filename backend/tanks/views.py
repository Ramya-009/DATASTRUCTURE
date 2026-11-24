from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Tank
from .serializers import TankSerializer

class TankListCreateView(APIView):
    def get(self, request):
        tanks = Tank.objects.all().order_by('tank_id')
        serializer = TankSerializer(tanks, many=True)
        total_capacity = sum(t.capacity for t in tanks)
        total_current = sum(t.current_level for t in tanks)
        overall_percentage = round((total_current / total_capacity * 100), 1) if total_capacity > 0 else 0.0

        return Response({
            'success': True,
            'count': tanks.count(),
            'total_capacity_litres': total_capacity,
            'total_current_level_litres': total_current,
            'overall_percentage': overall_percentage,
            'tanks': serializer.data
        })

    def post(self, request):
        serializer = TankSerializer(data=request.data)
        if serializer.is_valid():
            tank = serializer.save()
            return Response({
                'success': True,
                'message': f'Tank {tank.tank_name} ({tank.tank_id}) created successfully.',
                'tank': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TankDetailView(APIView):
    def get_object(self, pk):
        try:
            return Tank.objects.get(pk=pk)
        except Tank.DoesNotExist:
            return None

    def get(self, request, pk):
        tank = self.get_object(pk)
        if not tank:
            return Response({'success': False, 'message': 'Tank not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'tank': TankSerializer(tank).data})

    def put(self, request, pk):
        tank = self.get_object(pk)
        if not tank:
            return Response({'success': False, 'message': 'Tank not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TankSerializer(tank, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': f'Tank {tank.tank_id} updated successfully.',
                'tank': serializer.data
            })
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tank = self.get_object(pk)
        if not tank:
            return Response({'success': False, 'message': 'Tank not found.'}, status=status.HTTP_404_NOT_FOUND)
        tank.delete()
        return Response({'success': True, 'message': f'Tank {pk} deleted successfully.'})
