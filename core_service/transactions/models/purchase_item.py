from django.db import models
import uuid 

class PurchaseItem(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  purchase = models.ForeignKey(
    'transactions.Purchase',
    on_delete=models.CASCADE,
    related_name='items'
  )
  product = models.ForeignKey(
    'inventory.Product',
    on_delete=models.CASCADE,
    related_name='purchase_items'
  )
  item_purchase_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True) 
  quantity = models.DecimalField(max_digits=19, decimal_places=4)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'purchase_items'
    ordering = ['-created_at']
