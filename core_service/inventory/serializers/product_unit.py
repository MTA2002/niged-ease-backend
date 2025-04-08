from rest_framework import serializers
from inventory.models.product_unit import ProductUnit
from companies.serializers.company import CompanySerializer

class ProductUnitSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = ProductUnit
        fields = [
            'id', 'company', 'name', 
            'description', 'created_at', 
            'updated_at'
        ] 