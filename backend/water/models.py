from django.db import models
from django.conf import settings

class Area(models.Model):
    PRIORITY_CHOICES = (
        (1, 'Priority 1 - Emergency Zone'),
        (2, 'Priority 2 - Hospital / Healthcare Zone'),
        (3, 'Priority 3 - Essential Public Services'),
        (4, 'Priority 4 - Household / Residential Zone'),
        (5, 'Priority 5 - Commercial / Industrial Zone'),
        (6, 'Priority 6 - Low Priority Zone'),
    )

    area_name = models.CharField(max_length=120, unique=True)
    location = models.CharField(max_length=150)
    population = models.IntegerField(default=1000)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=4)
    daily_quota_litres = models.FloatField(default=50000.0, help_text="Target daily allocation in Litres")
    status = models.CharField(max_length=20, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.area_name} ({self.location}) - P{self.priority}"


class WaterRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Admin Review'),
        ('APPROVED', 'Approved by Admin'),
        ('ALLOCATED', 'Allocated by C Algorithm'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Water Supplied & Completed'),
    )

    PRIORITY_CHOICES = (
        (1, '1 - Emergency (Highest)'),
        (2, '2 - Hospital / Medical'),
        (3, '3 - Essential Public Services'),
        (4, '4 - Household / Domestic'),
        (5, '5 - Commercial / Business'),
        (6, '6 - Low Priority / Recreational'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='water_requests')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='water_requests')
    requested_quantity = models.FloatField(help_text="Requested Quantity in Litres")
    allocated_quantity = models.FloatField(default=0.0, help_text="Quantity allocated by C engine in Litres")
    request_date = models.DateField(help_text="Date when water is needed")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=4)
    reason = models.CharField(max_length=255, default='Household requirement')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Req #{self.id} - {self.user.name} ({self.requested_quantity}L) - {self.status}"


class WaterUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usage_records')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='usage_records')
    quantity = models.FloatField(help_text="Water consumed in Litres")
    usage_date = models.DateField()
    source = models.CharField(max_length=60, default='TAP_SUPPLY')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.quantity}L on {self.usage_date}"


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_items')
    rating = models.IntegerField(default=5)
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.name} - Rating {self.rating}/5"
