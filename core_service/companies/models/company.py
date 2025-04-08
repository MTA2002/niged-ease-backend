import uuid
from django.db import models


class Company(models.Model):

  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  name = models.CharField(max_length=30, unique=True)
  short_name = models.CharField(max_length=10)
  address = models.CharField(max_length=100)
  subscription_plan = models.ForeignKey('companies.SubscriptionPlan', on_delete=models.CASCADE, related_name='companies', null=False)
  currency = models.ForeignKey('companies.Currency', on_delete=models.CASCADE, related_name='companies', null=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)


  class Meta:
    db_table = 'companies'
    ordering = ['-created_at']
  
  def __str__(self):
     return f"{self.name}"