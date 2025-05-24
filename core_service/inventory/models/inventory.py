from django.db import models
import uuid
from decimal import Decimal
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import logging

from inventory.models.product import Product
from companies.models.store import Store

logger = logging.getLogger(__name__)
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
    low_stock_threshold = models.DecimalField(max_digits=19, decimal_places=4, default=Decimal('10'))
    low_stock_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventories'
        ordering = ['-created_at']
        unique_together = ['product', 'store']

    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

@receiver(pre_save, sender=Inventory)
def check_stock_level_change(sender, instance, **kwargs):
    """Check if stock is crossing the threshold"""
    if instance.pk:  # Only for updates
        try:
            old_instance = Inventory.objects.get(pk=instance.pk)
            
            # Reset notification flag if stock goes above threshold
            if instance.quantity > instance.low_stock_threshold:
                instance.low_stock_notified = False
            
            # Check if crossing from above to below threshold
            was_above_threshold = old_instance.quantity > old_instance.low_stock_threshold
            is_now_below_threshold = instance.quantity <= instance.low_stock_threshold
            
            if was_above_threshold and is_now_below_threshold and not instance.low_stock_notified:
                instance._should_notify = True
            else:
                instance._should_notify = False
                
        except Inventory.DoesNotExist:
            pass

@receiver(post_save, sender=Inventory)
def handle_low_stock_notification(sender, instance, created, **kwargs):
    """Send notification if stock is low"""
    if hasattr(instance, '_should_notify') and instance._should_notify:
        # Import here to avoid circular imports
        from core_service.rabbitmq_client import rabbitmq_client
        
        print(instance.store.company_id.id)
        # Prepare data for notification
        notification_data = {
            'inventory_id': str(instance.id),
            'product_name': instance.product.name,
            'store_name': instance.store.name,
            'current_quantity': float(instance.quantity),
            'threshold': float(instance.low_stock_threshold),
            'store_id': str(instance.store.id),
            'company_id': str(instance.store.company_id.id),
            'timestamp': timezone.now().isoformat()
        }
        
        # Send notification
        success = rabbitmq_client.send_low_stock_notification(notification_data)
        
        if success:
            # Mark as notified
            Inventory.objects.filter(pk=instance.pk).update(low_stock_notified=True)
            logger.info(f"Low stock notification sent for {instance.product.name}")
        else:
            logger.error(f"Failed to send notification for {instance.product.name}")