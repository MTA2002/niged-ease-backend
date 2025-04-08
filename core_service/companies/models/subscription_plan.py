import uuid
from django.db import models

class SubscriptionPlan(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=20)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    max_users = models.PositiveIntegerField(default=1)
    storage_limit_gb = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        db_table = 'subscription_plans'
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_cycle}"
