from rest_framework import serializers
from transactions.models.purchase_item import PurchaseItem
from transactions.serializers.purchase import PurchaseSerializer
from inventory.serializers.product import ProductSerializer


class PurchaseItemSerializer(serializers.ModelSerializer):
    purchase = PurchaseSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'purchase', 'product', 
            'quantity', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 