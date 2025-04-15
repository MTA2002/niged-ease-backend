from django.db import models
import uuid 
from decimal import Decimal
from inventory.models.inventory import Inventory

class Sale(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  store = models.ForeignKey('inventory.Store', on_delete=models.CASCADE)
  customer = models.ForeignKey('transactions.Customer', on_delete=models.PROTECT)
  total_amount = models.DecimalField(max_digits=19, decimal_places=4)
  currency = models.ForeignKey('companies.Currency', on_delete=models.SET_NULL, null=True)
  payment_mode = models.ForeignKey('transactions.PaymentMode', on_delete=models.SET_NULL, null=True)
  is_credit = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'sales'
    ordering = ['-created_at']

  def update_inventory(self, sale_items):
    """
    Update inventory quantities based on sale items.
    Decreases inventory quantities for each product sold.
    """
    for item in sale_items:
      try:
        inventory = Inventory.objects.get(
          product=item.product,
          store=self.store
        )
        inventory.quantity -= item.quantity
        if inventory.quantity < 0:
          raise ValueError(f"Insufficient inventory for product {item.product.name}")
        inventory.save()
      except Inventory.DoesNotExist:
        raise ValueError(f"No inventory record found for product {item.product.name} in store {self.store.name}")
