import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey('companies.SubscriptionPlan', on_delete=models.PROTECT)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f"{self.company.name} - {self.plan.name} Subscription"

    def save(self, *args, **kwargs):
        if not self.end_date:
            # Set end date to 1 month from start date
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.end_date

    def renew(self, months=1):
        """Renew the subscription for the specified number of months"""
        self.end_date = self.end_date + timedelta(days=30 * months)
        self.is_active = True
        self.save()
        self.company.is_subscribed = True
        self.company.save() 