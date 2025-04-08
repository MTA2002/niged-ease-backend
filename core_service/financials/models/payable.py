from django.db import models
import uuid

from companies.models.company import Company
from companies.models.currency import Currency
from transactions.models.purchase import Purchase

class Payable(models.Model):
  
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='company_payables',
    null=False
  )

  purchase = models.ForeignKey(
    Purchase,
    on_delete=models.CASCADE,
    related_name='purchase_payables',
    null=False
  )
  amount = models.DecimalField(max_digits=19, decimal_places=4)

  currency = models.ForeignKey(
    Currency,
    on_delete=models.CASCADE,
    related_name='payable_currency',
    null=False
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'payables'
    ordering = ['-created_at']
    
