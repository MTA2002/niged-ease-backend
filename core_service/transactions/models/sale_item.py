from django.db import models
import uuid 

class SaleItem(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  sale_id = models.ForeignKey('transactions.Sale', on_delete=models.CASCADE)
  product_id = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
  quantity = models.IntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'sale_items'