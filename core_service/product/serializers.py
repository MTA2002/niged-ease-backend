from rest_framework import serializers
from .models import ProductUnit, ProductCategory, Product

class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = ['id', 'company', 'name', 'description', 'created_at']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'company', 'name', 'description', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)
    unit = ProductUnitSerializer(read_only=True)
    unit_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = Product
        fields = ['id', 'company', 'name', 'description', 'category', 'category_id', 'unit', 'unit_id', 
                  'created_at', 'updated_at']