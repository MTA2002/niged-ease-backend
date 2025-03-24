from rest_framework import serializers
from .models import Store, Inventory
from product.serializers import ProductSerializer

class StoreSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True, required=False)  # Optional in payload

    class Meta:
        model = Store
        fields = ['id', 'company', 'name', 'location', 'created_at', 'updated_at', 'company_id']
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']  # company set via company_id

    def validate_company_id(self, value):
        from financial.models import Company
        if value and not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Company with id {value} does not exist.")
        return value

class InventorySerializer(serializers.ModelSerializer): 
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    store_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_id', 'store', 'store_id', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['id', 'product', 'store', 'created_at', 'updated_at']  # store set via store_id

