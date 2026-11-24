from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login, logout
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Registration successful! You can now log in.',
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'success': True,
                'message': f'Welcome back, {user.name}!',
                'user': UserProfileSerializer(user).data,
                'redirect_url': '/admin/dashboard/' if user.role == 'ADMIN' else '/user/dashboard/'
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': True, 'message': 'Logged out successfully.'})


class CurrentUserView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': UserProfileSerializer(request.user).data
            })
        return Response({'authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


class UserListView(APIView):
    """Admin can list and manage all registered users"""
    def get(self, request):
        users = CustomUser.objects.all().order_by('-date_joined')
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role)
        area_id = request.query_params.get('area_id')
        if area_id:
            users = users.filter(area_id=area_id)
        serializer = UserProfileSerializer(users, many=True)
        return Response({'success': True, 'count': users.count(), 'users': serializer.data})
