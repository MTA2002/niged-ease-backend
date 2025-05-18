from rest_framework import serializers
from companies.models.store import Store
from inventory.models.product_unit import ProductUnit
from companies.serializers.store import StoreSerializer

class ProductUnitSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = ProductUnit
        fields = [
            'id', 'store_id', 'store', 'name', 
            'description', 'created_at', 
            'updated_at'
        ]

    def create(self, validated_data):
        store_id = validated_data.pop('store_id')
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise serializers.ValidationError("Invalid store ID")
        
        return ProductUnit.objects.create(store_id=store, **validated_data)
