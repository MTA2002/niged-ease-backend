from django.db import models
import uuid

from companies.models.company import Company
from companies.models.currency import Currency
from transactions.models import Sale

class Receivable(models.Model):
  
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='company_receivables',
    null=False
  )

  sale = models.ForeignKey(
    Sale,
    on_delete=models.CASCADE,
    related_name='sale_receivables',
    null=False
  )
  amount = models.DecimalField(max_digits=19, decimal_places=4)

  currency = models.ForeignKey(
    Currency,
    on_delete=models.CASCADE,
    related_name='receivable_currency',
    null=False
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'receivables'
    ordering = ['-created_at']
    
