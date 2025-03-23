from rest_framework import serializers
from .models import Store, Inventory
from product.serializers import ProductSerializer

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'company', 'name', 'location', 'created_at', 'updated_at']

class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    store_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_id', 'store', 'store_id', 'quantity', 'created_at', 'updated_at']