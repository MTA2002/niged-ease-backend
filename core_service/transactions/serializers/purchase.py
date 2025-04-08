from rest_framework import serializers
from transactions.models.purchase import Purchase
from companies.serializers.company import CompanySerializer
from inventory.serializers.store import StoreSerializer
from transactions.serializers.supplier import SupplierSerializer
from companies.serializers.currency import CurrencySerializer
from financials.serializers.payment_mode import PaymentModeSerializer


class PurchaseSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    supplier = SupplierSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'company', 'store', 
            'supplier', 'total_amount', 
            'currency', 'payment_mode',
            'is_credit', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 