from rest_framework import serializers
from clothings.models.collection import Collection
from clothings.models.color import Color
from clothings.serializers.color import ColorSerializer
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
            'purchase_price','sale_price', 
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
            'product_category': {'required': True},
            'purchase_price': {'required': True},
            'sale_price': {'required': True}
        }

    def validate(self, attrs):
        sale_price = attrs.get('sale_price')
        purchase_price = attrs.get('purchase_price')
        if sale_price <= 0:
            raise serializers.ValidationError("Sale price must be a positive number.")
        if purchase_price <= 0:
            raise serializers.ValidationError("Purchase price must be a positive number.")
        
        if sale_price < purchase_price:
            raise serializers.ValidationError("Sale price must be greater than purchase price.")
        
        return super().validate(attrs)

    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        color_id = validated_data.pop('color_id')
        collection_id = validated_data.pop('collection_id')

        try:
            company = Company.objects.get(id=company_id)
            color = Color.objects.get(id=color_id)
            collection = Collection.objects.get(id=collection_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return Product.objects.create(company_id=company, color_id = color, collection_id = collection, **validated_data) 