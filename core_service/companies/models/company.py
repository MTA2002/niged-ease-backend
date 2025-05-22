import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .subscription_plan import SubscriptionPlan


class Company(models.Model):

  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  address = models.CharField(max_length=255,default='')
  name = models.CharField(max_length=100, unique=True)
  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)
  is_subscribed = models.BooleanField(default=False)  # Ensure this is not null
  
  # Subscription fields
  subscription_plan = models.ForeignKey(
    SubscriptionPlan,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='companies'
  )
  subscription_start_date = models.DateTimeField(null=True, blank=True)
  subscription_expiration_date = models.DateTimeField(null=True, blank=True)
  company_profile_image = models.URLField(max_length=255, default='', null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  class Meta:
    db_table = 'companies'
    verbose_name_plural = 'companies'
  
  def __str__(self):
     return self.name

  def is_subscription_valid(self):
    """Check if the company's subscription is still valid"""
    if not self.subscription_expiration_date:
      return False
    return timezone.now() <= self.subscription_expiration_date

  def check_subscription_limits(self, entity_type, current_count):
    """
    Check if the company has reached its subscription limits
    entity_type: 'products', 'stores', or 'users'
    current_count: how many the company currently has
    """
    if not self.is_subscription_valid() or not self.subscription_plan:
      return False
            
    max_allowed = getattr(self.subscription_plan, f'max_{entity_type}', 0)
    return current_count < max_allowed

  def renew_subscription(self, months=None):
    """Renew the subscription for the specified number of months"""
    now = timezone.now()
    self.subscription_start_date = now
    duration = months or (self.subscription_plan.duration_in_months if self.subscription_plan else 1)
    self.subscription_expiration_date = now + timedelta(days=30 * duration)
    self.save()
    return True