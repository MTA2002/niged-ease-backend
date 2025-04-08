from rest_framework import serializers
from transactions.models.sale_item import SaleItem
from transactions.serializers.sale import SaleSerializer
from inventory.serializers.product import ProductSerializer


class SaleItemSerializer(serializers.ModelSerializer):
    sale = SaleSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'sale', 'product', 
            'quantity', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 