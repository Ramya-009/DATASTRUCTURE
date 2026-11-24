from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('USER', 'Customer / Citizen'),
        ('ADMIN', 'Water System Administrator'),
    )

    name = models.CharField(max_length=150, help_text="Full name of citizen or admin")
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    area = models.ForeignKey('water.Area', on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    house_number = models.CharField(max_length=50, blank=True, default='')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    daily_water_quota_litres = models.FloatField(default=350.0, help_text="Standard daily allocated quota per household")
    status = models.CharField(max_length=20, default='ACTIVE')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"

    @property
    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_staff or self.is_superuser
