from rest_framework import serializers
from companies.models.company import Company
from inventory.models.product_unit import ProductUnit
from companies.serializers.company import CompanySerializer

class ProductUnitSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = ProductUnit
        fields = [
            'id', 'company_id', 'company', 'name', 
            'description', 'created_at', 
            'updated_at'
        ]

    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return ProductUnit.objects.create(company_id=company, **validated_data)
