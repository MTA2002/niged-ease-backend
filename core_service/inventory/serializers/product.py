from rest_framework import serializers
from inventory.models.product import Product
from companies.serializers.company import CompanySerializer
from inventory.serializers.product_unit import ProductUnitSerializer
from inventory.serializers.product_category import ProductCategorySerializer
from companies.models.company import Company

class ProductSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    company = CompanySerializer(read_only=True)
    product_unit = ProductUnitSerializer(read_only=True)
    product_category = ProductCategorySerializer(read_only=True)
    product_unit_id = serializers.UUIDField(write_only=True)
    product_category_id = serializers.UUIDField(write_only=True)
    color_id = serializers.UUIDField(write_only=True)
    collection_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'company_id', 'company', 'name', 
            'description', 'image',
            'product_unit', 'product_category',
            'product_unit_id', 'product_category_id',
            'color_id', 'collection_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company_id': {'required': True},
            'color_id': {'required': True},
            'collection_id': {'required': True},
            'name': {'required': True},
            'product_unit': {'required': True},
            'product_category': {'required': True}
        }

    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return Product.objects.create(company_id=company, **validated_data) 