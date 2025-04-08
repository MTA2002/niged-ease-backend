from django.db import models
import uuid 

class Purchase(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  store = models.ForeignKey('inventory.Store', on_delete=models.CASCADE)
  supplier = models.ForeignKey('transactions.Supplier', on_delete=models.PROTECT)
  total_amount = models.DecimalField(max_digits=19, decimal_places=4)
  currency = models.ForeignKey('companies.Currency', on_delete=models.SET_NULL, null=True)
  payment_mode = models.ForeignKey('financials.PaymentMode', on_delete=models.SET_NULL, null=True)
  is_credit = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'purchases'
    ordering = ['-created_at']
