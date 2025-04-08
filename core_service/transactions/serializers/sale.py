from rest_framework import serializers
from transactions.models import Sale
from companies.serializers.company import CompanySerializer
from inventory.serializers.store import StoreSerializer
from transactions.serializers.customer import CustomerSerializer
from companies.serializers.currency import CurrencySerializer
from financials.serializers.payment_mode import PaymentModeSerializer


class SaleSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'company', 'store', 
            'customer', 'total_amount', 
            'currency', 'payment_mode',
            'is_credit', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 