from rest_framework import serializers
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
            'is_credit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company_id': {'required': True},
            'store_id': {'required': True},
            'supplier_id': {'required': True},
            'total_amount': {'required': True}
        }

    def create(self, validated_data):
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
            
            if currency_id:
                currency = Currency.objects.get(id=currency_id)
                purchase.currency = currency # type: ignore
                
            if payment_mode_id:
                payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                purchase.payment_mode = payment_mode # type: ignore
                
            purchase.save()
            return purchase
            
        except (Company.DoesNotExist, Store.DoesNotExist, Supplier.DoesNotExist,
                Currency.DoesNotExist, PaymentMode.DoesNotExist) as e:
            raise serializers.ValidationError(str(e)) 