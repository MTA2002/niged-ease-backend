from django.db import models, transaction
import uuid 
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
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
  tax = models.DecimalField(
    max_digits=5, 
    decimal_places=2, 
    default=Decimal('0.00'),
    validators=[MinValueValidator(0), MaxValueValidator(100)],
    help_text="Tax percentage (0-100)"
  )
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

  def delete(self, *args, **kwargs):
    """
    Override delete method to handle associated records properly.
    This will:
    1. Reduce inventory quantities
    2. Delete associated payment records
    3. Delete payables
    4. Delete purchase items
    """
    from financials.models.payable import Payable
    from financials.models.payment_out import PaymentOut
    from transactions.models.purchase_item import PurchaseItem

    with transaction.atomic():
      # Get all associated records before deletion
      purchase_items = PurchaseItem.objects.filter(purchase=self)
      payables = Payable.objects.filter(purchase=self)
      payments = PaymentOut.objects.filter(purchase=self)

      # Reduce inventory quantities
      for item in purchase_items:
        try:
          inventory = Inventory.objects.select_for_update().get(
            product=item.product,
            store=self.store_id
          )
          inventory.quantity -= item.quantity
          # Check if we have enough quantity to remove
          if inventory.quantity < 0:
            raise ValueError(f"Cannot delete purchase: Would result in negative inventory for product {item.product.name}")
          inventory.save()
        except Inventory.DoesNotExist:
          # If no inventory exists, we can safely continue as there's nothing to reduce
          pass

      # Delete associated records
      payments.delete()  # Delete payment records
      payables.delete()  # Delete payables
      purchase_items.delete()  # Delete purchase items

      # Finally delete the purchase itself
      super().delete(*args, **kwargs)
