import uuid
from django.db import models
from .subscription_plan import SubscriptionPlan


class Company(models.Model):

  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)
  is_subscribed = models.BooleanField(default=False)
  current_subscription = models.ForeignKey(
    'companies.Subscription',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='companies'
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  class Meta:
    db_table = 'companies'
    verbose_name_plural = 'companies'
  
  def __str__(self):
     return self.name

  def check_subscription_limits(self, entity_type):
    """
    Check if the company has reached its subscription limits
    entity_type: 'companies' or 'stores'
    """
    if not self.is_subscribed or not self.current_subscription:
      return False
            
    plan = self.current_subscription.plan
    current_count = getattr(self, f'{entity_type}_count', 0)
    max_allowed = plan.features.get(f'max_{entity_type}', 0)
        
    return current_count < max_allowed