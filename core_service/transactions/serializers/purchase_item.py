from rest_framework import serializers
from transactions.models.purchase_item import PurchaseItem
from transactions.serializers.purchase import PurchaseSerializer
from inventory.serializers.product import ProductSerializer
from transactions.models.purchase import Purchase
from inventory.models.product import Product


class PurchaseItemSerializer(serializers.ModelSerializer):
    purchase_id = serializers.UUIDField(write_only=True)
    product_id = serializers.UUIDField(write_only=True)
    purchase = PurchaseSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'purchase_id', 'purchase', 'product_id', 'product', 
            'item_purchase_price','quantity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'purchase_id': {'required': True},
            'product_id': {'required': True},
            'quantity': {'required': True}
        }

    def create(self, validated_data):
        purchase_id = validated_data.pop('purchase_id')
        product_id = validated_data.pop('product_id')
        
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            product = Product.objects.get(id=product_id)
            
            return PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                **validated_data
            )
        except (Purchase.DoesNotExist, Product.DoesNotExist) as e:
            raise serializers.ValidationError(str(e)) 