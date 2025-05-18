import uuid
from django.db import models

class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    billing_cycle = models.CharField(
        max_length=10,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'
    )
    duration_in_months = models.PositiveIntegerField(default=1)
    max_products = models.IntegerField(default=0)
    max_users = models.IntegerField(default=0)
    max_stores = models.IntegerField(default=0)
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    storage_limit_gb = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.billing_cycle})"

    class Meta:
        ordering = ['price'] 