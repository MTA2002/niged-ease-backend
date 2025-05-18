from django.db import models
import uuid

from companies.models.store import Store
from companies.models.currency import Currency
from transactions.models.payment_mode import PaymentMode
from transactions.models import Sale
from financials.models.receivable import Receivable

class PaymentIn(models.Model):
  
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  store_id = models.ForeignKey(
    Store,
    on_delete=models.CASCADE,
    related_name='store_payment_ins',
    null=False
  )

  receivable = models.ForeignKey(
    Receivable,
    on_delete=models.CASCADE,
    related_name='receivable_payment_ins',
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
    
