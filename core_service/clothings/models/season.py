from django.db import models
import uuid

class Season(models.Model):
  id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
  company_id = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
  name = models.CharField(max_length=100, unique=True)
  start_date = models.DateField()
  end_date = models.DateField()
  description = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    db_table = 'seasons'
    unique_together = ('company_id', 'name')


  def __str__(self):
    return self.name
