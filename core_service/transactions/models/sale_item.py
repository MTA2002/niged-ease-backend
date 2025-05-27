from django.db import models
import uuid 

class SaleItem(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  sale = models.ForeignKey(
    'transactions.Sale',
    on_delete=models.CASCADE,
    related_name='items'
  )
  product = models.ForeignKey(
    'inventory.Product',
    on_delete=models.CASCADE,
    related_name='sale_items'
  )
  item_sale_price = models.DecimalField(max_digits=19, decimal_places=4, null=True, blank=True) 
  quantity = models.DecimalField(max_digits=19, decimal_places=4)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'sale_items'
    ordering = ['-created_at']