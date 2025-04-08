import uuid
from django.db import models
from companies.models.company import Company


class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='expense_categories',
        null=False
    )
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'expense_categories'
        unique_together = ['company', 'name']
        

    def __str__(self):
        return f"{self.name} - {self.company.name}"
