# type: ignore
from rest_framework import serializers
from django.db import models
from inventory.models.product import Product
from transactions.models import Purchase
from companies.serializers.company import CompanySerializer
from inventory.serializers.store import StoreSerializer
from transactions.serializers.supplier import SupplierSerializer
from companies.serializers.currency import CurrencySerializer
from transactions.serializers.payment_mode import PaymentModeSerializer
from companies.models.company import Company
from inventory.models.store import Store
from transactions.models.supplier import Supplier
from companies.models.currency import Currency
from transactions.models.payment_mode import PaymentMode
from transactions.models.purchase_item import PurchaseItem
from financials.models.payable import Payable
from inventory.models.inventory import Inventory

class PurchaseSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    store_id = serializers.UUIDField(write_only=True)
    supplier_id = serializers.UUIDField(write_only=True)
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
    supplier = SupplierSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'company_id', 'company', 'store_id', 'store', 
            'supplier_id', 'supplier', 'total_amount', 
            'currency_id', 'currency', 'payment_mode_id', 'payment_mode',
            'is_credit', 'created_at', 'updated_at','items',
            'status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['items']
        extra_kwargs = {
            'company_id': {'required': True},
            'store_id': {'required': True},
            'supplier_id': {'required': True},
            'total_amount': {'required': True}
        }
    
    def validate(self, data):
        """
        Validate that the payable and purchase belong to the same company
        and the payment amount is valid.
        """
        company_id = data.get('company_id')
        store_id = data.get('store_id')
        supplier_id = data.get('supplier_id')
        given_amount = data.get('total_amount')
        actual_amount = 0

        # Validate that the total amount is a positive number
        if given_amount < 0:
            raise serializers.ValidationError("Total amount must be a positive number.")
        
        if 'items' not in data:
            raise serializers.ValidationError("Items are required to create a purchase.")
        
        if data['items'] is None:
            raise serializers.ValidationError("Items cannot be null.")
        if not isinstance(data['items'], list):
            raise serializers.ValidationError("Items must be a list.")
        if len(data['items']) == 0:
            raise serializers.ValidationError("Items cannot be an empty list.")
        
        for item in data.get('items', []):
            product_id = item.get('product_id')
            try:
                quantity = int(item.get('quantity', 0))
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantity must be a valid integer.")
                
            if product_id is None:
                raise serializers.ValidationError("Product cannot be null.")
            if quantity is None:
                raise serializers.ValidationError("Quantity cannot be null.")
            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            if not isinstance(product_id, str):
                raise serializers.ValidationError("Product ID must be a string.")
            
            product = Product.objects.filter(id=product_id).first()
            if product and quantity:
                actual_amount += product.purchase_price * quantity
        
        print("Actual Amount:", actual_amount)
        print("Given Amount:", given_amount)
        if given_amount > actual_amount:
            raise serializers.ValidationError("Given amount exceeds the actual amount.")

        if given_amount < 0:
            raise serializers.ValidationError("Given amount cannot be negative.")
        
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        company_id = validated_data.pop('company_id')
        store_id = validated_data.pop('store_id')
        supplier_id = validated_data.pop('supplier_id')
        currency_id = validated_data.pop('currency_id', None)
        payment_mode_id = validated_data.pop('payment_mode_id', None)
        total_amount = validated_data.get('total_amount')
        actual_amount = 0

        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.purchase_price * quantity
        
        print('actual_amount', actual_amount)
        print('total_amount', total_amount)
        try:
            company = Company.objects.get(id=company_id)
            store = Store.objects.get(id=store_id)
            supplier = Supplier.objects.get(id=supplier_id)
            
            if total_amount <= 0:
                status = Purchase.PurchaseStatus.UNPAID
            elif total_amount < actual_amount:
                status = Purchase.PurchaseStatus.PARTIALLY_PAID
            else:
                status = Purchase.PurchaseStatus.PAID

            purchase = Purchase.objects.create(
                status=status,
                company=company,
                store=store,
                supplier=supplier,
                **validated_data
            )
            
            currency = None
            if currency_id:
                currency = Currency.objects.get(id=currency_id)
                purchase.currency = currency
                
            if payment_mode_id:
                payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                purchase.payment_mode = payment_mode
            
            # Create PurchaseItem instances and update inventory
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = int(item_data['quantity'])
                
                # Create purchase item
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=quantity
                )
                
                # Update or create inventory
                try:
                    inventory = Inventory.objects.get(product=product, store=store)
                    inventory.quantity += quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    Inventory.objects.create(
                        product=product,
                        store=store,
                        quantity=quantity
                    )
            
            # Create payable if not fully paid
            if status in [Purchase.PurchaseStatus.UNPAID, Purchase.PurchaseStatus.PARTIALLY_PAID]:
                payable_amount = actual_amount - total_amount
                Payable.objects.create(
                    company=company,
                    purchase=purchase,
                    amount=payable_amount,
                    currency=currency or purchase.currency
                )
            
            purchase.save()
            return purchase
            
        except (Company.DoesNotExist, Store.DoesNotExist, Supplier.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist, Product.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Update a Purchase instance and its associated items."""
        items_data = validated_data.pop('items', [])
        actual_amount = 0
        total_amount = validated_data.get('total_amount', instance.total_amount)

        # Calculate actual amount from items
        for item in items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.purchase_price * quantity

        # Determine purchase status based on amount
        if total_amount <= 0:
            status = Purchase.PurchaseStatus.UNPAID
        elif total_amount < actual_amount:
            status = Purchase.PurchaseStatus.PARTIALLY_PAID
        else:
            status = Purchase.PurchaseStatus.PAID

        # Update the instance fields
        instance.status = status
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Handle items update if provided
        if items_data:
            # First, reverse inventory quantities from old items
            old_items = PurchaseItem.objects.filter(purchase=instance)
            for old_item in old_items:
                inventory = Inventory.objects.get(product=old_item.product, store=instance.store)
                inventory.quantity -= old_item.quantity
                inventory.save()
            
            # Delete old items
            old_items.delete()
            
            # Create new items and update inventory
            for item_data in items_data:
                product = Product.objects.get(id=item_data['product_id'])
                quantity = item_data['quantity']
                
                # Create new purchase item
                PurchaseItem.objects.create(
                    purchase=instance,
                    product=product,
                    quantity=quantity
                )
                
                # Update or create inventory
                try:
                    inventory = Inventory.objects.get(product=product, store=instance.store)
                    inventory.quantity += quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    Inventory.objects.create(
                        product=product,
                        store=instance.store,
                        quantity=quantity
                    )

        # Handle payable update
        try:
            payable = Payable.objects.get(purchase=instance)
            if status == Purchase.PurchaseStatus.PAID:
                # Delete payable if fully paid
                payable.delete()
            else:
                # Update payable amount
                payable_amount = actual_amount - total_amount
                payable.amount = payable_amount
                payable.save()
        except Payable.DoesNotExist:
            # Create new payable if not fully paid
            if status in [Purchase.PurchaseStatus.UNPAID, Purchase.PurchaseStatus.PARTIALLY_PAID]:
                payable_amount = actual_amount - total_amount
                Payable.objects.create(
                    company=instance.company,
                    purchase=instance,
                    amount=payable_amount,
                    currency=instance.currency
                )

        return instance 