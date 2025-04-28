from django.db import models
import uuid
from decimal import Decimal
from inventory.models.store import Store

class Product(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  company_id = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  color_id = models.ForeignKey('clothings.Color', on_delete=models.CASCADE)
  collection_id = models.ForeignKey('clothings.Collection', on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  description = models.TextField(null=True)
  image = models.URLField(null=True)
  product_unit = models.ForeignKey('inventory.ProductUnit', on_delete=models.PROTECT)
  product_category = models.ForeignKey('inventory.ProductCategory', on_delete=models.PROTECT)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'products'

 
    
    