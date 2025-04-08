from rest_framework import serializers
from inventory.models.product import Product
from companies.serializers.company import CompanySerializer
from inventory.serializers.product_unit import ProductUnitSerializer
from inventory.serializers.product_category import ProductCategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    product_unit = ProductUnitSerializer(read_only=True)
    product_category = ProductCategorySerializer(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'company', 'name', 
            'description', 'image',
            'product_unit', 'product_category',
            'created_at', 'updated_at'
        ] 