from rest_framework import serializers
from inventory.models.product_category import ProductCategory
from companies.serializers.company import CompanySerializer

class ProductCategorySerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'company', 'name', 
            'description', 'created_at', 
            'updated_at'
        ] 