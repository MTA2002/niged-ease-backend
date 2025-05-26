from django.db import models
import uuid

class Store(models.Model):

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  company_id = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  name = models.CharField(max_length=30, unique=True)
  is_active = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
  ], default='active')
  location = models.CharField(max_length=30)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    db_table = 'stores' 