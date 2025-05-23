from rest_framework import serializers
from inventory.models.product import Product
from inventory.models.inventory import Inventory
from companies.serializers.store import StoreSerializer
from inventory.serializers.product_unit import ProductUnitSerializer
from inventory.serializers.product_category import ProductCategorySerializer

class ProductSearchResultSerializer(serializers.ModelSerializer):
    store = StoreSerializer(source='store_id', read_only=True)
    product_unit = ProductUnitSerializer(read_only=True)
    product_category = ProductCategorySerializer(read_only=True)
    inventory = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image',
            'store', 'product_unit', 'product_category',
            'purchase_price', 'sale_price', 'inventory',
            'created_at', 'updated_at'
        ]
    
    def get_inventory(self, obj):
        """Get inventory details for this product across all stores with positive inventory"""
        # Only include positive inventory counts
        inventories = Inventory.objects.filter(
            product=obj,
            quantity__gt=0
        ).select_related('store')
        
        inventory_data = []
        for inv in inventories:
            inventory_data.append({
                'store_id': str(inv.store.id),
                'store_name': inv.store.name,
                'store_location': inv.store.location,
                'quantity': inv.quantity
            })
            
        return inventory_data 