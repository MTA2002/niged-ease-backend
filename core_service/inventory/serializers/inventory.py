from rest_framework import serializers
from inventory.models.inventory import Inventory
from inventory.models.product import Product
from companies.models.store import Store
from inventory.serializers.product import ProductSerializer
from companies.serializers.store import StoreSerializer

class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    store_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Inventory
        fields = [
            'id', 'product_id', 'product', 'store_id', 'store',
            'quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'product_id': {'required': True},
            'store_id': {'required': True},
            'quantity': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the product belongs to the given store.
        """
        product_id = data.get('product_id')
        store_id = data.get('store_id')
        
        try:
            product = Product.objects.get(id=product_id)
            store = Store.objects.get(id=store_id)
        except (Product.DoesNotExist, Store.DoesNotExist):
            raise serializers.ValidationError("Invalid product or store ID")
        
        if product.store_id.id != store.id:
            raise serializers.ValidationError(
                "Product must belong to the specified store"
            )
        
        return data

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        store_id = validated_data.pop('store_id')
        
        product = Product.objects.get(id=product_id)
        store = Store.objects.get(id=store_id)
        
        return Inventory.objects.create(
            product=product,
            store=store,
            **validated_data
        ) 