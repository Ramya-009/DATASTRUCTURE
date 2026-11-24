from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    area_name = serializers.CharField(source='area.area_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'password', 'mobile', 'address', 'area', 'area_name', 'house_number', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        # Derive username from email or name
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = CustomUser(**validated_data)
        user.username = username
        user.set_password(password)
        if user.role == 'ADMIN':
            user.is_staff = True
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.area_name', read_only=True, default='')

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'mobile', 'address', 'area', 'area_name', 'house_number', 'role', 'status', 'daily_water_quota_litres', 'date_joined']
        read_only_fields = ['id', 'role', 'date_joined']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')

            if not user.check_password(password):
                raise serializers.ValidationError('Invalid email or password.')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include both email and password.')
