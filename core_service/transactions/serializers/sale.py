# type: ignore
from rest_framework import serializers
from inventory.models.product import Product
from transactions.models import Sale
from companies.serializers.company import CompanySerializer
from inventory.serializers.store import StoreSerializer
from transactions.serializers.customer import CustomerSerializer
from companies.serializers.currency import CurrencySerializer
from transactions.serializers.payment_mode import PaymentModeSerializer
from companies.models.company import Company
from inventory.models.store import Store
from transactions.models.customer import Customer
from companies.models.currency import Currency
from transactions.models.payment_mode import PaymentMode
from transactions.models.sale_item import SaleItem
from financials.models.receivable import Receivable


class SaleSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
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
    company = CompanySerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'company_id', 'company', 'store_id', 'store', 
            'customer_id', 'customer', 'total_amount', 
            'currency_id', 'currency', 'payment_mode_id', 'payment_mode',
            'is_credit', 'created_at', 'updated_at', 'status',
            'items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status']
        extra_kwargs = {
            'company_id': {'required': True},
            'store_id': {'required': True},
            'customer_id': {'required': True},
            
        }

    def validate(self, attrs):
        """
        Validate the input data for creating a Sale.
        Ensure that the company, store, and customer exist.
        """
        company_id = attrs.get('company_id')
        store_id = attrs.get('store_id')
        customer_id = attrs.get('customer_id')
        given_amount = attrs.get('total_amount')
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
            quantity = int(item.get('quantity', 0))
            print("Product ID:", product_id)
            print("Quantity:", quantity)
            if product_id is None:
                raise serializers.ValidationError("Product cannot be null.")
            if quantity is None:
                raise serializers.ValidationError("Quantity cannot be null.")
            print(not isinstance(quantity, int), quantity)
            if not isinstance(quantity, int) or quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            if not isinstance(product_id, str):
                raise serializers.ValidationError("Product ID must be a string.")
            
            product = Product.objects.filter(id=product_id).first()
            if Inventory.objects.filter(product=product, store=store_id).first().quantity < quantity:
                raise serializers.ValidationError("Insufficient quantity in inventory.")
            
            if product and quantity:
                actual_amount += product.sale_price * quantity
        
        print("Actual Amount:", actual_amount)
        if given_amount > actual_amount:
            raise serializers.ValidationError("Given amount exceeds the actual amount.")
        
        if given_amount < 0:
            raise serializers.ValidationError("Given amount cannot be negative.")
        try:
            Company.objects.get(id=company_id)
            Store.objects.get(id=store_id)
            Customer.objects.get(id=customer_id)
        except (Company.DoesNotExist, Store.DoesNotExist, Customer.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

        return super().validate(attrs)
    
    def create(self, validated_data):
        # Extract items and related IDs from validated data
        items_data = validated_data.pop('items')
        company_id = validated_data.pop('company_id')
        store_id = validated_data.pop('store_id')
        customer_id = validated_data.pop('customer_id')
        currency_id = validated_data.pop('currency_id', None)
        payment_mode_id = validated_data.pop('payment_mode_id', None)
        total_amount = validated_data.get('total_amount')
        
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

        try:
            # Fetch related objects
            company = Company.objects.get(id=company_id)
            store = Store.objects.get(id=store_id)
            customer = Customer.objects.get(id=customer_id)
            
            # Determine sale status based on amount received
            if total_amount <= 0:
                status = Sale.SaleStatus.UNPAID
            elif total_amount < actual_amount:
                status = Sale.SaleStatus.PARTIALLY_PAID
            else:
                status = Sale.SaleStatus.PAID
            
            # Create the Sale instance
            sale = Sale.objects.create(
                company=company,
                store=store,
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
            
            # Create SaleItem instances from items data
            for item_data in items_data:
                SaleItem.objects.create(
                    sale=sale,
                    product=Product.objects.get(id=item_data['product_id']),
                    quantity=item_data['quantity']
                )
            
            # Create receivable if not fully paid
            if status in [Sale.SaleStatus.UNPAID, Sale.SaleStatus.PARTIALLY_PAID]:
                receivable_amount = actual_amount - total_amount
                Receivable.objects.create(
                    company=company,
                    sale=sale,
                    amount=receivable_amount,
                    currency=currency or sale.currency
                )
            
            sale.save()
            return sale
            
        except (Company.DoesNotExist, Store.DoesNotExist, Customer.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist, Product.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Update a Sale instance and its associated items."""
        items_data = validated_data.pop('items', [])
        actual_amount = 0
        total_amount = validated_data.get('total_amount', instance.total_amount)

        # Calculate actual amount from items
        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.sale_price * quantity

        # Determine sale status based on amount
        if total_amount <= 0:
            status = Sale.SaleStatus.UNPAID
        elif total_amount < actual_amount:
            status = Sale.SaleStatus.PARTIALLY_PAID
        else:
            status = Sale.SaleStatus.PAID

        # Update the instance fields
        instance.status = status
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Handle items update if provided
        if items_data:
            # First, delete existing items
            instance.saleitem_set.all().delete()
            
            # Create new items
            for item_data in items_data:
                SaleItem.objects.create(
                    sale=instance,
                    product=Product.objects.get(id=item_data['product_id']),
                    quantity=item_data['quantity']
                )

        # Handle receivable update
        try:
            receivable = Receivable.objects.get(sale=instance)
            if status == Sale.SaleStatus.PAID:
                # Delete receivable if fully paid
                receivable.delete()
            else:
                # Update receivable amount
                receivable_amount = actual_amount - total_amount
                receivable.amount = receivable_amount
                receivable.save()
        except Receivable.DoesNotExist:
            # Create new receivable if not fully paid
            if status in [Sale.SaleStatus.UNPAID, Sale.SaleStatus.PARTIALLY_PAID]:
                receivable_amount = actual_amount - total_amount
                Receivable.objects.create(
                    company=instance.company,
                    sale=instance,
                    amount=receivable_amount,
                    currency=instance.currency
                )

        return instance 
