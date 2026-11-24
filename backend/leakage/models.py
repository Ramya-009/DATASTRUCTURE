from django.db import models
from django.conf import settings

class LeakageReport(models.Model):
    STATUS_CHOICES = (
        ('REPORTED', 'Reported'),
        ('UNDER_REVIEW', 'Under Review'),
        ('REPAIRING', 'Repair Team Dispatched'),
        ('RESOLVED', 'Resolved & Repaired'),
    )

    SEVERITY_CHOICES = (
        ('MINOR', 'Minor (Slow Seepage)'),
        ('MODERATE', 'Moderate Leak'),
        ('HIGH', 'High Pressure Burst'),
        ('CRITICAL', 'Critical Pipeline Emergency'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_leaks')
    area = models.ForeignKey('water.Area', on_delete=models.CASCADE, related_name='leakage_reports')
    location = models.CharField(max_length=200, help_text="Street address / Landmark of suspected leak")
    description = models.TextField()
    reported_date = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    loss_volume_litres = models.FloatField(default=0.0, help_text="Estimated water lost per hour in Litres")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')
    admin_comment = models.TextField(blank=True, default='')
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Leak #{self.id} at {self.location} ({self.status}) - {self.severity}"
