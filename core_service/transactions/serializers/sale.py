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


class SaleSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    store_id = serializers.UUIDField(write_only=True)
    customer_id = serializers.UUIDField(write_only=True)
    currency_id = serializers.UUIDField(write_only=True, required=False)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    
    company = CompanySerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'company_id', 'company', 'store_id', 'store', 
            'customer_id', 'customer', 'total_amount', 
            'currency_id', 'currency', 'payment_mode_id', 'payment_mode',
            'is_credit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company_id': {'required': True},
            'store_id': {'required': True},
            'customer_id': {'required': True},
            'total_amount': {'required': True}
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
        if given_amount <= 0:
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
            quantity = item.get('quantity')
            if product_id is None:
                raise serializers.ValidationError("Product cannot be null.")
            if quantity is None:
                raise serializers.ValidationError("Quantity cannot be null.")
            if not isinstance(quantity, int) or quantity <= 0:
                raise serializers.ValidationError("Quantity must be a positive integer.")
            if not isinstance(product_id, str):
                raise serializers.ValidationError("Product ID must be a string.")
            
            product = Product.objects.filter(id=product).first()

            if product and quantity:
                actual_amount += product.sale_price * quantity
        
        if actual_amount != given_amount:
            raise serializers.ValidationError("Total amount does not match the sum of item prices.")
        
        try:
            Company.objects.get(id=company_id)
            Store.objects.get(id=store_id)
            Customer.objects.get(id=customer_id)
        except (Company.DoesNotExist, Store.DoesNotExist, Customer.DoesNotExist) as e:
            raise serializers.ValidationError(str(e))

        return super().validate(attrs)
    
    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        store_id = validated_data.pop('store_id')
        customer_id = validated_data.pop('customer_id')
        currency_id = validated_data.pop('currency_id', None)
        payment_mode_id = validated_data.pop('payment_mode_id', None)
        
        try:
            company = Company.objects.get(id=company_id)
            store = Store.objects.get(id=store_id)
            customer = Customer.objects.get(id=customer_id)
            
            sale = Sale.objects.create(
                company=company,
                store=store,
                customer=customer,
                **validated_data
            )
            
            if currency_id:
                currency = Currency.objects.get(id=currency_id)
                sale.currency = currency # type: ignore
                
            if payment_mode_id:
                payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                sale.payment_mode = payment_mode # type: ignore
                
            sale.save()
            return sale
            
        except (Company.DoesNotExist, Store.DoesNotExist, Customer.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist) as e:
            raise serializers.ValidationError(str(e)) 