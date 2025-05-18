from django.db import models
import uuid 
from decimal import Decimal
from inventory.models.inventory import Inventory

class Purchase(models.Model):
  class PurchaseStatus(models.TextChoices):
    UNPAID = 'UNPAID', 'Unpaid'
    PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
    PAID = 'PAID', 'Paid'

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  store_id = models.ForeignKey('companies.Store', on_delete=models.CASCADE)
  supplier = models.ForeignKey('transactions.Supplier', on_delete=models.PROTECT)
  total_amount = models.DecimalField(max_digits=19, decimal_places=4)
  currency = models.ForeignKey('companies.Currency', on_delete=models.SET_NULL, null=True)
  payment_mode = models.ForeignKey('transactions.PaymentMode', on_delete=models.SET_NULL, null=True)
  status = models.CharField(max_length=15, choices=PurchaseStatus.choices, default=PurchaseStatus.UNPAID)
  is_credit = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    db_table = 'purchases'
    ordering = ['-created_at']

  def update_inventory(self, purchase_items):
    """
    Update inventory quantities based on purchase items.
    Increases inventory quantities for each product purchased.
    """
    for item in purchase_items:
      try:
        inventory = Inventory.objects.get(
          product=item.product,
          store=self.store_id
        )
        inventory.quantity += item.quantity
        inventory.save()
      except Inventory.DoesNotExist:
        # If inventory doesn't exist, create a new record
        Inventory.objects.create(
          product=item.product,
          store=self.store_id,
          quantity=item.quantity
        )
