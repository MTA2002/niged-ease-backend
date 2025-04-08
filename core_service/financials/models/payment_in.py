from django.db import models
import uuid

from companies.models.company import Company
from companies.models.currency import Currency
from financials.models.payment_mode import PaymentMode
from transactions.models import Sale
from transactions.models.purchase import Purchase

class PaymentIn(models.Model):
  
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='company_payment_ins',
    null=False
  )

  receivable = models.ForeignKey(
    Purchase,
    on_delete=models.CASCADE,
    related_name='purchase_payment_ins',
    null=False
  )

  sale = models.ForeignKey(
    Sale,
    on_delete=models.CASCADE,
    related_name='sale_payment_ins',
    null=False
  )

  amount = models.DecimalField(max_digits=19, decimal_places=4)

  currency = models.ForeignKey(
    Currency,
    on_delete=models.CASCADE,
    related_name='payment_in_currency',
    null=False
  )

  payment_mode = models.ForeignKey(
    PaymentMode,
    on_delete=models.CASCADE,
    related_name='payment_in_modes',
    null=False
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'payment_ins'
    ordering = ['-created_at']
    
