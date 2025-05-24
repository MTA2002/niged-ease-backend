from django.db import models
import uuid
from companies.models.store import Store
class Color(models.Model):
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  store_id = models.ForeignKey('companies.Store', on_delete=models.CASCADE)
  name = models.CharField(max_length=100)
  color_code = models.CharField(max_length=7, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  is_active = models.BooleanField(default=True)
  
  class Meta:
    db_table = 'colors'
    unique_together = ['store_id', 'name']

  def __str__(self):
    return self.name
