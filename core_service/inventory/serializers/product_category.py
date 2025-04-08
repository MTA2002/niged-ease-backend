from rest_framework import serializers
from inventory.models.product_category import ProductCategory
from companies.serializers.company import CompanySerializer
from companies.models.company import Company

class ProductCategorySerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'company_id', 'company', 'name', 
            'description', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company_id': {'required': True},
            'name': {'required': True}
        }

    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return ProductCategory.objects.create(company_id=company, **validated_data) 