import uuid
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class SubscriptionPlan(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    PLAN_TYPES = [
        ('free', 'Free'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    storage_limit_gb = models.IntegerField(default=5)
    max_products = models.PositiveIntegerField(default=0)
    max_stores = models.PositiveIntegerField(default=0)
    max_customers = models.PositiveIntegerField(default=0)
    duration_in_months = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} ({self.billing_cycle})"
    
    @classmethod
    def get_default_plans(cls):
        return [
            {
                'name': 'free',
                'description': 'Basic plan with limited features',
                'price': 0.00,
                'features': {
                    'max_products': 50,
                    'max_stores': 2,
                    'max_customers': 1,
                    'storage_limit_gb': 5
                }
            },
            {
                'name': 'standard',
                'description': 'Standard plan with moderate features',
                'price': 29.99,
                'features': {
                    'max_products': 500,
                    'max_stores': 10,
                    'max_customers': 5,
                    'storage_limit_gb': 20
                }
            },
            {
                'name': 'premium',
                'description': 'Premium plan with all features',
                'price': 99.99,
                'features': {
                    'max_products': 5000,
                    'max_stores': 50,
                    'max_customers': 20,
                    'storage_limit_gb': 100
                }
            }
        ]
