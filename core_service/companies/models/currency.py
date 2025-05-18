from django.db import models
import uuid

class Currency(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=15, unique=True)
  code = models.CharField(max_length=5, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
      db_table = 'currencies'
      
  def str(self):
     return f"{self.name} {self.code}"