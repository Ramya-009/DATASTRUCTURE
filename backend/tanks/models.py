from django.db import models

class Tank(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active / Operational'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('OFFLINE', 'Offline / Empty'),
    )

    tank_id = models.CharField(max_length=50, unique=True, help_text="Unique Tank Code, e.g. T001")
    tank_name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    capacity = models.FloatField(help_text="Total storage capacity in Litres")
    current_level = models.FloatField(help_text="Current water stored in Litres")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def water_level_percentage(self):
        if self.capacity and self.capacity > 0:
            return round((self.current_level / self.capacity) * 100, 1)
        return 0.0

    @property
    def available_water_litres(self):
        return max(0.0, self.current_level)

    def __str__(self):
        return f"{self.tank_id} - {self.tank_name} ({self.water_level_percentage}%)"
