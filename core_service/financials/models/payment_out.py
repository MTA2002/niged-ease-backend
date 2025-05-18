from django.db import models
import uuid

from companies.models.store import Store
from companies.models.currency import Currency
from financials.models.payable import Payable
from transactions.models.payment_mode import PaymentMode
from transactions.models.purchase import Purchase

class PaymentOut(models.Model):
  
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  store_id = models.ForeignKey(
    Store,
    on_delete=models.CASCADE,
    related_name='store_payment_outs',
    null=False
  )

  payable = models.ForeignKey(
    Payable,
    on_delete=models.CASCADE,
    related_name='payable_payment_outs',
    null=False
  )

  purchase = models.ForeignKey(
    Purchase,
    on_delete=models.CASCADE,
    related_name='purchase_payment_outs',
    null=False
  )

  amount = models.DecimalField(max_digits=19, decimal_places=4)

  currency = models.ForeignKey(
    Currency,
    on_delete=models.CASCADE,
    related_name='payment_out_currency',
    null=False
  )

  payment_mode = models.ForeignKey(
    PaymentMode,
    on_delete=models.CASCADE,
    related_name='payment_out_modes',
    null=False
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'payment_outs'
    ordering = ['-created_at']
    
