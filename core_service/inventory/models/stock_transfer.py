from django.db import models
import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone

class StockTransfer(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    source_store = models.ForeignKey(
        'companies.Store',
        on_delete=models.PROTECT,
        related_name='outgoing_transfers'
    )
    destination_store = models.ForeignKey(
        'companies.Store',
        on_delete=models.PROTECT,
        related_name='incoming_transfers'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        related_name='transfers'
    )
    quantity = models.DecimalField(max_digits=19, decimal_places=4)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_transfers'
        ordering = ['-created_at']


    def __str__(self):
        return f"Transfer {self.quantity} of {self.product} from {self.source_store} to {self.destination_store}" 