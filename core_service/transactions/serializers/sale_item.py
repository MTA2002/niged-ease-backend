from rest_framework import serializers
from transactions.models.sale_item import SaleItem
from inventory.serializers.product import ProductSerializer
from transactions.models.sale import Sale
from inventory.models.product import Product


class SaleItemSerializer(serializers.ModelSerializer):
    sale = serializers.UUIDField(write_only=True)
    product_id = serializers.UUIDField(write_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'sale', 'product_id', 'product', 
            'item_sale_price', 'quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'sale': {'required': True},
            'product_id': {'required': True},
            'quantity': {'required': True}
        }

    def create(self, validated_data):
        sale_id = validated_data.pop('sale')
        product_id = validated_data.pop('product_id')
        
        try:
            sale = Sale.objects.get(id=sale_id)
            product = Product.objects.get(id=product_id)
            
            return SaleItem.objects.create(
                sale=sale,
                product=product,
                **validated_data
            )
        except (Sale.DoesNotExist, Product.DoesNotExist) as e:
            raise serializers.ValidationError(str(e)) 