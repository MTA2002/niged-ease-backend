from rest_framework import serializers
from inventory.models.inventory import Inventory
from inventory.models.product import Product
from inventory.models.store import Store
from inventory.serializers.product import ProductSerializer
from inventory.serializers.store import StoreSerializer
from companies.models.company import Company

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
        Validate that the product and store belong to the same company.
        """
        product_id = data.get('product_id')
        store_id = data.get('store_id')
        
        try:
            product = Product.objects.get(id=product_id)
            store = Store.objects.get(id=store_id)
        except (Product.DoesNotExist, Store.DoesNotExist):
            raise serializers.ValidationError("Invalid product or store ID")
        
        if product.company != store.company: # type: ignore
            raise serializers.ValidationError(
                "Product and store must belong to the same company"
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