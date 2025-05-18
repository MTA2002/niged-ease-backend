from django.db import models
import uuid

from companies.models.store import Store
from companies.models.currency import Currency
from financials.models.expense_category import ExpenseCategory
from transactions.models.payment_mode import PaymentMode


class Expense(models.Model):
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  store_id = models.ForeignKey(
    Store,
    on_delete=models.CASCADE,
    related_name='store_expenses',
    null=False
  )
  expense_category = models.ForeignKey(
    ExpenseCategory,
    on_delete=models.CASCADE,
    related_name='expenses',
    null=False
  )
  amount = models.DecimalField(max_digits=19, decimal_places=4)

  currency = models.ForeignKey(
    Currency,
    on_delete=models.CASCADE,
    related_name='expense_currency',
    null=False
  )

  payment_mode = models.ForeignKey(
    PaymentMode,
    on_delete=models.CASCADE,
    related_name='expense_payments',
    null=False
  )

  description = models.TextField(null=True, blank=True)
  is_credit = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'expenses'
    ordering = ['-created_at']
    