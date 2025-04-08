from django.db import models
import uuid 

class PurchaseItem(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  purchase_id = models.ForeignKey('transactions.Purchase', on_delete=models.CASCADE)
  product_id = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
  quantity = models.IntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'purchase_items'
