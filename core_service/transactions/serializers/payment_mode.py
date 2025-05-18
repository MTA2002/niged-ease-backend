from rest_framework import serializers
from transactions.models.payment_mode import PaymentMode
from inventory.serializers.store import StoreSerializer


class PaymentModeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentMode
        fields = [
            'id',
            'store_id',
            'name',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the payment mode name is unique within the store.
        """
        name = data.get('name')
        store_id = data.get('store_id')
        
        # Check if another payment mode with the same name exists in this store
        existing = PaymentMode.objects.filter(name=name, store_id=store_id)
        
        # If we're updating, exclude the current instance
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
            
        if existing.exists():
            raise serializers.ValidationError(
                "A payment mode with this name already exists in this store."
            )
        return data 