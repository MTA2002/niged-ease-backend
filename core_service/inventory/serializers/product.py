from rest_framework import serializers
from clothings.models.collection import Collection
from clothings.models.color import Color
from clothings.serializers.color import ColorSerializer
from clothings.serializers.collection import CollectionSerializer
from inventory.models.product import Product
from companies.models.store import Store
from companies.serializers.store import StoreSerializer
from inventory.serializers.product_unit import ProductUnitSerializer
from inventory.serializers.product_category import ProductCategorySerializer

class ProductSerializer(serializers.ModelSerializer):
   
    product_unit = ProductUnitSerializer(read_only=True)
    product_category = ProductCategorySerializer(read_only=True)
    product_unit_id = serializers.UUIDField(write_only=True)
    product_category_id = serializers.UUIDField(write_only=True)
    color_id = serializers.UUIDField(write_only=True)
    collection_id = serializers.UUIDField(write_only=True)
    
    # Add method fields for color and collection details
    color = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [ 
            'id', 'store_id', 'name', 
            'description', 'image',
            'product_unit', 'product_category', 
            'product_unit_id', 'product_category_id', 
            'purchase_price','sale_price', 
            'color_id', 'collection_id',
            'color', 'collection',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'color_id': {'required': True},
            'collection_id': {'required': True},
            'name': {'required': True},
            'product_unit': {'required': True},
            'product_category': {'required': True},
            'purchase_price': {'required': True},
            'sale_price': {'required': True}
        }
        
    def get_color(self, obj):
        """Get the color details"""
        color = Color.objects.get(id=obj.color_id.id)
        return ColorSerializer(color).data
        
    def get_collection(self, obj):
        """Get the collection details"""
        collection = Collection.objects.get(id=obj.collection_id.id)
        return CollectionSerializer(collection).data

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
        color_id = validated_data.pop('color_id')
        collection_id = validated_data.pop('collection_id')

        try:
            color = Color.objects.get(id=color_id)
            collection = Collection.objects.get(id=collection_id)
        except (Color.DoesNotExist, Collection.DoesNotExist):
            raise serializers.ValidationError("Invalid color or collection ID")
        
        return Product.objects.create(color_id=color, collection_id=collection, **validated_data) 
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.product_unit_id = validated_data.get('product_unit_id', instance.product_unit_id)
        instance.product_category_id = validated_data.get('product_category_id', instance.product_category_id)
        instance.purchase_price = validated_data.get('purchase_price', instance.purchase_price)
        instance.sale_price = validated_data.get('sale_price', instance.sale_price)
        instance.color_id = Color.objects.get(id=validated_data.get('color_id', instance.color_id))
        instance.collection_id = Collection.objects.get(id=validated_data.get('collection_id', instance.collection_id))
        instance.save()
        return instance