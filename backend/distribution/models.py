from django.db import models

class DistributionSchedule(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    area = models.ForeignKey('water.Area', on_delete=models.CASCADE, related_name='schedules')
    tank = models.ForeignKey('tanks.Tank', on_delete=models.CASCADE, related_name='distribution_runs')
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    allocated_quantity = models.FloatField(help_text="Volume to be distributed in Litres")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule #{self.id} - {self.area.area_name} on {self.scheduled_date} ({self.allocated_quantity} L)"
