from rest_framework import serializers
from inventory.models.product_category import ProductCategory
from companies.serializers.store import StoreSerializer
from companies.models.store import Store

class ProductCategorySerializer(serializers.ModelSerializer):
    

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'store_id', 'name', 
            'description', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'name': {'required': True}
        }

    # def create(self, validated_data):
    #     store_id = validated_data.pop('store_id')
    #     try:
    #         store = Store.objects.get(id=store_id)
    #     except Store.DoesNotExist:
    #         raise serializers.ValidationError("Invalid store ID")
        
    #     return ProductCategory.objects.create(store_id=store, **validated_data) 