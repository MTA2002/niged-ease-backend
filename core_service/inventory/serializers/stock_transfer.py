from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from inventory.models.stock_transfer import StockTransfer
from inventory.models.inventory import Inventory
from inventory.models.product import Product

class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransfer
        fields = ['id', 'source_store', 'destination_store', 'product', 
                 'quantity', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        # Check if source and destination stores are different
        if data['source_store'] == data['destination_store']:
            raise serializers.ValidationError(
                "Cannot transfer stock to the same store"
            )

        # Check if quantity is positive
        if data['quantity'] <= 0:
            raise serializers.ValidationError(
                "Transfer quantity must be greater than 0"
            )

        # Check if source store has sufficient stock
        try:
            source_inventory = Inventory.objects.get(
                store=data['source_store'],
                product=data['product']
            )
            
          
            required_quantity = data['quantity']
                
            if source_inventory.quantity < required_quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock in source store. Available: {source_inventory.quantity}"
                )
        except Inventory.DoesNotExist:
            raise serializers.ValidationError(
                "Product not found in source store's inventory"
            )

        return data

    def _ensure_destination_product_exists(self, source_product, destination_store):
        """
        Ensure the product exists in the destination store.
        If not, create it by copying from the source product.
        """
        try:
            return Product.objects.get(
                store_id=destination_store,
                name=source_product.name
            )
        except Product.DoesNotExist:
            # Create new product in destination store
            destination_product = Product.objects.create(
                store_id=destination_store,
                name=source_product.name,
                description=source_product.description,
                image=source_product.image,
                product_unit=source_product.product_unit,
                purchase_price=source_product.purchase_price,
                sale_price=source_product.sale_price,
                product_category=source_product.product_category,
                color_id=source_product.color_id,
                collection_id=source_product.collection_id
            )
            return destination_product

    @transaction.atomic
    def create(self, validated_data):
        # First ensure the product exists in destination store
        source_product = validated_data['product']
        destination_product = self._ensure_destination_product_exists(
            source_product, 
            validated_data['destination_store']
        )
        
        # Create the transfer record
        transfer = StockTransfer.objects.create(**validated_data)
        
        # Update source inventory
        source_inventory = Inventory.objects.select_for_update().get(
            store=validated_data['source_store'],
            product=validated_data['product']
        )
        source_inventory.quantity -= Decimal(str(validated_data['quantity']))
        source_inventory.save()

        # Create or update destination inventory
        destination_inventory, created = Inventory.objects.select_for_update().get_or_create(
            store=validated_data['destination_store'],
            product=destination_product,
            defaults={'quantity': Decimal('0')}
        )
        destination_inventory.quantity += Decimal(str(validated_data['quantity']))
        destination_inventory.save()

        # Mark transfer as completed
        transfer.status = StockTransfer.COMPLETED
        transfer.save()

        return transfer

    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.status == StockTransfer.CANCELLED:
            raise serializers.ValidationError(
                "Canceled transfers can't be updated"
            )

        # First ensure the product exists in destination store
        source_product = validated_data['product']
        destination_product = self._ensure_destination_product_exists(
            source_product, 
            validated_data['destination_store']
        )

        # Revert old source inventory
        old_source_inventory = Inventory.objects.select_for_update().get(
            store=instance.source_store,
            product=instance.product
        )
        old_source_inventory.quantity += Decimal(str(instance.quantity))
        old_source_inventory.save()

        # Revert old destination inventory
        old_destination_inventory = Inventory.objects.select_for_update().get(
            store=instance.destination_store,
            product=instance.product
        )
        old_destination_inventory.quantity -= Decimal(str(instance.quantity))
        old_destination_inventory.save()

        # Apply new transfer quantities
        new_source_inventory = Inventory.objects.select_for_update().get(
            store=validated_data['source_store'],
            product=validated_data['product']
        )
        new_source_inventory.quantity -= Decimal(str(validated_data['quantity']))
        new_source_inventory.save()

        # Create or update new destination inventory
        new_destination_inventory, created = Inventory.objects.select_for_update().get_or_create(
            store=validated_data['destination_store'],
            product=destination_product,
            defaults={'quantity': Decimal('0')}
        )
        new_destination_inventory.quantity += Decimal(str(validated_data['quantity']))
        new_destination_inventory.save()

        # Update the transfer record
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance