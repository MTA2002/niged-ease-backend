from django.db import models
import uuid

class ProductUnit(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  company_id = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  name = models.CharField(max_length=30)
  description = models.TextField(null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'product_units'