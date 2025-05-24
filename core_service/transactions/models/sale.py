from django.db import models, transaction
import uuid 
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from inventory.models.inventory import Inventory

class Sale(models.Model):
  class SaleStatus(models.TextChoices):
    UNPAID = 'UNPAID', 'Unpaid'
    PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
    PAID = 'PAID', 'Paid'

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  store_id = models.ForeignKey('companies.Store', on_delete=models.CASCADE)
  customer = models.ForeignKey('transactions.Customer', on_delete=models.PROTECT)
  total_amount = models.DecimalField(max_digits=19, decimal_places=4)
  tax = models.DecimalField(
    max_digits=5, 
    decimal_places=2, 
    default=Decimal('0.00'),
    validators=[MinValueValidator(0), MaxValueValidator(100)],
    help_text="Tax percentage (0-100)"
  )
  currency = models.ForeignKey('companies.Currency', on_delete=models.SET_NULL, null=True)
  payment_mode = models.ForeignKey('transactions.PaymentMode', on_delete=models.SET_NULL, null=True)
  is_credit = models.BooleanField(default=False)
  status = models.CharField(
    max_length=20,
    choices=SaleStatus.choices,
    default=SaleStatus.UNPAID
  )
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
          store=self.store_id
        )
        inventory.quantity -= item.quantity
        if inventory.quantity < 0:
          raise ValueError(f"Insufficient inventory for product {item.product.name}")
        inventory.save()
      except Inventory.DoesNotExist:
        raise ValueError(f"No inventory record found for product {item.product.name} in store {self.store_id.name}")

  def delete(self, *args, **kwargs):
    """
    Override delete method to handle associated records properly.
    This will:
    1. Return inventory quantities
    2. Delete associated payment records
    3. Delete receivables
    4. Delete sale items
    """
    from financials.models.receivable import Receivable
    from financials.models.payment_in import PaymentIn
    from transactions.models.sale_item import SaleItem

    with transaction.atomic():
      # Get all associated records before deletion
      sale_items = SaleItem.objects.filter(sale=self)
      receivables = Receivable.objects.filter(sale=self)
      payments = PaymentIn.objects.filter(sale=self)

      # Return inventory quantities
      for item in sale_items:
        try:
          inventory = Inventory.objects.select_for_update().get(
            product=item.product,
            store=self.store_id
          )
          inventory.quantity += item.quantity
          inventory.save()
        except Inventory.DoesNotExist:
          # Create inventory if it doesn't exist
          Inventory.objects.create(
            product=item.product,
            store=self.store_id,
            quantity=item.quantity
          )

      # Delete associated records
      payments.delete()  # Delete payment records
      receivables.delete()  # Delete receivables
      sale_items.delete()  # Delete sale items

      # Finally delete the sale itself
      super().delete(*args, **kwargs)
