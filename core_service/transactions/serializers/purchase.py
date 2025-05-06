from rest_framework import serializers
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
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'company_id', 'company', 'store_id', 'store', 
            'supplier_id', 'supplier', 'total_amount', 
            'currency_id', 'currency', 'payment_mode_id', 'payment_mode',
            'is_credit', 'created_at', 'updated_at','items'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        write_only_fields = ['items']
        extra_kwargs = {
            'company_id': {'required': True},
            'store_id': {'required': True},
            'supplier_id': {'required': True},
            'total_amount': {'required': True}
        }
    
    def validate(self, attrs):
        """
        Validate the input data for creating a Purchase.
        Ensure that the company, store, and supplier exist.
        """
        company_id = attrs.get('company_id')
        store_id = attrs.get('store_id')
        supplier_id = attrs.get('supplier_id')
        
        try:
            Company.objects.get(id=company_id)
            Store.objects.get(id=store_id)
            Supplier.objects.get(id=supplier_id)
        except (Company.DoesNotExist, Store.DoesNotExist, Supplier.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

        given_amount = attrs.get('total_amount')
        actual_amount = 0

        # Validate that the total amount is a positive number
        if given_amount <= 0:
            raise serializers.ValidationError("Total amount must be a positive number.")
        
        if 'items' not in attrs:
            raise serializers.ValidationError("Items are required to create a purhase.")
        
        if attrs['items'] is None:
            raise serializers.ValidationError("Items cannot be null.")
        if not isinstance(attrs['items'], list):
            raise serializers.ValidationError("Items must be a list.")
        if len(attrs['items']) == 0:
            raise serializers.ValidationError("Items cannot be an empty list.")
        
        
        for item in attrs.get('items', []):
            product_id = item.get('product_id')
            quantity = int(item.get('quantity'))
            if product_id is None:
                raise serializers.ValidationError("Product cannot be null.")
            if quantity is None:
                raise serializers.ValidationError("Quantity cannot be null.")
            if not isinstance(quantity, int) or quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            if not isinstance(product_id, str):
                raise serializers.ValidationError("Product ID must be a string.")
            
            product = Product.objects.filter(id=product_id).first()

            if product and quantity:
                actual_amount += product.purchase_price * quantity
        print("Actual Amount:", actual_amount)
        if actual_amount != given_amount:
            raise serializers.ValidationError("Total amount does not match the sum of item prices.")
        
        return attrs
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        company_id = validated_data.pop('company_id')
        store_id = validated_data.pop('store_id')
        supplier_id = validated_data.pop('supplier_id')
        currency_id = validated_data.pop('currency_id', None)
        payment_mode_id = validated_data.pop('payment_mode_id', None)
        
        try:
            company = Company.objects.get(id=company_id)
            store = Store.objects.get(id=store_id)
            supplier = Supplier.objects.get(id=supplier_id)
            
            purchase = Purchase.objects.create(
                company=company,
                store=store,
                supplier=supplier,
                **validated_data
            )
            
            print("Purchase Created:", purchase)
            if currency_id:
                currency = Currency.objects.get(id=currency_id)
                purchase.currency = currency # type: ignore
                
            if payment_mode_id:
                payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                purchase.payment_mode = payment_mode # type: ignore
                
            

            from transactions.models.purchase_item import PurchaseItem
            from inventory.models.product import Product
            
            for item_data in items_data:
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=Product.objects.get(id=item_data['product_id']),
                    quantity=item_data['quantity']
                )
            
            purchase.save()
            
        
            return purchase
            
        except (Company.DoesNotExist, Store.DoesNotExist, Supplier.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        """Update a Purchase instance and its associated PurchaseItems."""
        # Extract items and related IDs from validated data
        items_data = validated_data.pop('items', [])
        
        # Update the Purchase instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Create new PurchaseItem instances from items data
        from transactions.models.purchase_item import PurchaseItem
        from inventory.models.product import Product
        
        for item_data in items_data:
            PurchaseItem.objects.create(
                purchase=instance,
                product=Product.objects.get(id=item_data['product_id']),
                quantity=item_data['quantity']
            )
        
        return instance 