from rest_framework import serializers
from .models import ProductUnit, ProductCategory, Product

class ProductUnitSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)  # Add this to accept company_id directly

    class Meta:
        model = ProductUnit
        fields = ['id', 'company', 'name', 'description', 'created_at', 'company_id']
        read_only_fields = ['id', 'company', 'created_at']  # company is read-only, set via company_id

    def validate_company_id(self, value):
        from financial.models import Company
        if not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Company with id {value} does not exist.")
        return value

class ProductCategorySerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True, required=False)  # Make it optional

    class Meta:
        model = ProductCategory
        fields = ['id', 'company', 'name', 'description', 'created_at', 'company_id']
        read_only_fields = ['id', 'company', 'created_at']  # company is read-only, set via company_id

    def validate_company_id(self, value):
        from financial.models import Company
        if value and not Company.objects.filter(id=value).exists():  # Only validate if provided
            raise serializers.ValidationError(f"Company with id {value} does not exist.")
        return value 
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)
    unit = ProductUnitSerializer(read_only=True)
    unit_id = serializers.UUIDField(write_only=True, required=False)
    company_id = serializers.UUIDField(write_only=True)  # Add this to accept company_id directly

    class Meta:
        model = Product
        fields = ['id', 'company', 'name', 'description', 'category', 'category_id', 'unit', 'unit_id', 
                  'created_at', 'updated_at', 'company_id']
        read_only_fields = ['id', 'company', 'created_at', 'updated_at']  # company is read-only, set via company_id

    def validate_company_id(self, value):
        from financial.models import Company
        if not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Company with id {value} does not exist.")
        return value