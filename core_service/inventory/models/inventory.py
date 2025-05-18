from django.db import models
import uuid
from decimal import Decimal

from inventory.models.product import Product
from companies.models.store import Store

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        null=False
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='inventory_items',
        null=False
    )
    quantity = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventories'
        ordering = ['-created_at']
        unique_together = ['product', 'store'] 