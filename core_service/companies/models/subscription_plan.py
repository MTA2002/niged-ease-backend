import uuid
from django.db import models

class SubscriptionPlan(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
    ]
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=20, choices=PLAN_TYPES)
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
    
    @classmethod
    def get_default_plans(cls):
        return [
            {
                'name': 'free',
                'description': 'Basic plan with limited features',
                'price': 0.00,
                'features': {
                    'max_companies': 1,
                    'max_stores': 2,
                    'max_users': 1,
                    'storage_limit_gb': 5
                }
            },
            {
                'name': 'standard',
                'description': 'Standard plan with moderate features',
                'price': 29.99,
                'features': {
                    'max_companies': 3,
                    'max_stores': 10,
                    'max_users': 5,
                    'storage_limit_gb': 20
                }
            },
            {
                'name': 'premium',
                'description': 'Premium plan with all features',
                'price': 99.99,
                'features': {
                    'max_companies': 10,
                    'max_stores': 50,
                    'max_users': 20,
                    'storage_limit_gb': 100
                }
            }
        ]
