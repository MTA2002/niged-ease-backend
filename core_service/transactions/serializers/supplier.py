from rest_framework import serializers
from transactions.models.supplier import Supplier
from inventory.serializers.store import StoreSerializer


class SupplierSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'store_id', 'name', 'email', 
            'phone', 'address', 
            'credit_limit', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 