# type: ignore
from rest_framework import serializers
from inventory.models.product import Product
from transactions.models import Sale
from inventory.serializers.store import StoreSerializer
from transactions.serializers.customer import CustomerSerializer
from companies.serializers.currency import CurrencySerializer
from transactions.serializers.payment_mode import PaymentModeSerializer
from companies.models.store import Store
from inventory.models.inventory import Inventory
from transactions.models.customer import Customer
from companies.models.currency import Currency
from transactions.models.payment_mode import PaymentMode
from transactions.models.sale_item import SaleItem
from financials.models.receivable import Receivable
from decimal import Decimal


class SaleSerializer(serializers.ModelSerializer):
    store_id = serializers.UUIDField(write_only=True)
    customer_id = serializers.UUIDField(write_only=True)
    currency_id = serializers.UUIDField(write_only=True, required=False)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    items = serializers.ListField(
        write_only=True,
        child=serializers.DictField(
            child=serializers.CharField()
        ),
    )
    store = StoreSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'store_id', 'store', 
            'customer_id', 'customer', 'total_amount', 'tax',
            'currency_id', 'currency', 'payment_mode_id', 'payment_mode',
            'is_credit', 'created_at', 'updated_at', 'status',
            'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
        extra_kwargs = {
            'store_id': {'required': True},
            'customer_id': {'required': True},
            'tax': {'required': False}
        }

    def validate(self, attrs):
        """
        Validate the input data for creating a Sale.
        Ensure that the store and customer exist.
        """
        store_id = attrs.get('store_id')
        customer_id = attrs.get('customer_id')
        given_amount = attrs.get('total_amount')
        tax_rate = attrs.get('tax', 0)
        actual_amount = 0

        # Validate that the total amount is a positive number
        if given_amount < 0:
            raise serializers.ValidationError("Total amount must be a positive number.")
        
        if 'items' not in attrs:
            raise serializers.ValidationError("Items are required to create a sale.")
        
        if attrs['items'] is None:
            raise serializers.ValidationError("Items cannot be null.")
        if not isinstance(attrs['items'], list):
            raise serializers.ValidationError("Items must be a list.")
        if len(attrs['items']) == 0:
            raise serializers.ValidationError("Items cannot be an empty list.")
        
        
        for item in attrs.get('items', []):
            product_id = item.get('product_id')
            try:
                quantity = int(item.get('quantity', 0))
                item_sale_price = Decimal(str(item.get('item_sale_price'))) if item.get('item_sale_price') is not None else None
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity must be a valid integer and item_sale_price must be a valid decimal.")
                
            if product_id is None:
                raise serializers.ValidationError("Product cannot be null.")
            if quantity is None:
                raise serializers.ValidationError("Quantity cannot be null.")
            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            if not isinstance(product_id, str):
                raise serializers.ValidationError("Product ID must be a string.")
            
            product = Product.objects.filter(id=product_id).first()
            if not product:
                raise serializers.ValidationError(f"Product with id {product_id} does not exist.")

            # Validate item_sale_price if provided
            if item_sale_price is not None and item_sale_price < product.sale_price:
                raise serializers.ValidationError(f"Item sale price ({item_sale_price}) cannot be less than product sale price ({product.sale_price})")

            if product and quantity:
                # Use item_sale_price if provided, otherwise use product's sale_price
                price_to_use = item_sale_price if item_sale_price is not None else product.sale_price
                actual_amount += price_to_use * quantity
        
        # Apply tax to the actual amount
        actual_amount_with_tax = actual_amount + (actual_amount * (tax_rate / Decimal('100.0')))
        
        print("Actual Amount:", actual_amount)
        print("Actual Amount with Tax:", actual_amount_with_tax)
        print("Given Amount:", given_amount)
        if given_amount > actual_amount_with_tax:
            raise serializers.ValidationError("Given amount exceeds the actual amount.")
        
        if given_amount < 0:
            raise serializers.ValidationError("Given amount cannot be negative.")
        try:
            Store.objects.get(id=store_id)
            Customer.objects.get(id=customer_id)
        except (Store.DoesNotExist, Customer.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

        return super().validate(attrs)
    
    def create(self, validated_data):
        # Extract items and related IDs from validated data
        items_data = validated_data.pop('items')
        store_id = validated_data.pop('store_id')
        customer_id = validated_data.pop('customer_id')
        currency_id = validated_data.pop('currency_id', None)
        payment_mode_id = validated_data.pop('payment_mode_id', None)
        total_amount = validated_data.get('total_amount')
        tax_rate = validated_data.get('tax', 0)
        
        actual_amount = 0
        print('items_data', items_data)
        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            print('product_id', product_id)
            print('quantity', quantity)
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.sale_price * quantity
        
        # Apply tax to the actual amount
        actual_amount_with_tax = actual_amount + (actual_amount * (tax_rate / Decimal('100.0')))

        try:
            # Fetch related objects
            store = Store.objects.get(id=store_id)
            customer = Customer.objects.get(id=customer_id)
            
            # Determine sale status based on amount received
            if total_amount <= 0:
                status = Sale.SaleStatus.UNPAID
            elif total_amount < actual_amount_with_tax:
                status = Sale.SaleStatus.PARTIALLY_PAID
            else:
                status = Sale.SaleStatus.PAID
            
            # Create the Sale instance
            sale = Sale.objects.create(
                store_id=store,
                customer=customer,
                status=status,
                **validated_data
            )
            
            # Set optional related fields
            currency = None
            if currency_id:
                currency = Currency.objects.get(id=currency_id)
                sale.currency = currency
            if payment_mode_id:
                payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                sale.payment_mode = payment_mode
            
            # Create SaleItem instances and update inventory
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = int(item_data['quantity'])
                item_sale_price = Decimal(str(item_data.get('item_sale_price'))) if item_data.get('item_sale_price') is not None else None
                
                # Create sale item
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    item_sale_price=item_sale_price
                )
                
                # Update inventory
                inventory = Inventory.objects.get(product=product, store=store)
                inventory.quantity -= quantity
                inventory.save()
            
            # Create receivable if not fully paid
            if status in [Sale.SaleStatus.UNPAID, Sale.SaleStatus.PARTIALLY_PAID]:
                receivable_amount = actual_amount_with_tax - total_amount
                Receivable.objects.create(
                    store_id=store,
                    sale=sale,
                    amount=receivable_amount,
                    currency=currency or sale.currency
                )
            
            sale.save()
            return sale
            
        except (Store.DoesNotExist, Customer.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist, Product.DoesNotExist,
                Inventory.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Update a Sale instance and its associated items."""
        items_data = validated_data.pop('items', [])
        actual_amount = 0
        total_amount = validated_data.get('total_amount', instance.total_amount)
        tax_rate = validated_data.get('tax', instance.tax)

        # Calculate actual amount from items
        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.sale_price * quantity
        
        # Apply tax to the actual amount
        actual_amount_with_tax = actual_amount + (actual_amount * (tax_rate / Decimal('100.0')))

        # Determine sale status based on amount
        if total_amount <= 0:
            status = Sale.SaleStatus.UNPAID
        elif total_amount < actual_amount_with_tax:
            status = Sale.SaleStatus.PARTIALLY_PAID
        else:
            status = Sale.SaleStatus.PAID

        # Update the instance fields
        instance.status = status
        for attr, value in validated_data.items():
            if attr != 'store_id':  # Skip store_id updates
                setattr(instance, attr, value)
        
        instance.save()

        # Handle items update if provided
        if items_data:
            # First, restore inventory quantities from old items
            old_items = SaleItem.objects.filter(sale=instance)
            for old_item in old_items:
                inventory = Inventory.objects.get(product=old_item.product, store=instance.store)
                inventory.quantity += old_item.quantity
                inventory.save()
            
            # Delete old items
            old_items.delete()
            
            # Create new items and update inventory
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = int(item_data['quantity'])
                
                # Validate inventory
                inventory = Inventory.objects.get(product=product, store=instance.store)
                if inventory.quantity < quantity:
                    raise serializers.ValidationError(f"Insufficient inventory for product {product.name}")
                
                # Create new sale item
                SaleItem.objects.create(
                    sale=instance,
                    product=product,
                    quantity=quantity
                )
                
                # Update inventory
                inventory.quantity -= quantity
                inventory.save()

        # Handle receivable update
        try:
            receivable = Receivable.objects.get(sale=instance)
            if status == Sale.SaleStatus.PAID:
                # Delete receivable if fully paid
                receivable.delete()
            else:
                # Update receivable amount
                receivable_amount = actual_amount_with_tax - total_amount
                receivable.amount = receivable_amount
                receivable.save()
        except Receivable.DoesNotExist:
            # Create new receivable if not fully paid
            if status in [Sale.SaleStatus.UNPAID, Sale.SaleStatus.PARTIALLY_PAID]:
                receivable_amount = actual_amount_with_tax - total_amount
                Receivable.objects.create(
                    store_id=instance.store,
                    sale=instance,
                    amount=receivable_amount,
                    currency=instance.currency
                )

        return instance 
