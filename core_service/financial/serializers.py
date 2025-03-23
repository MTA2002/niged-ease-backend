from rest_framework import serializers
from .models import (
    PaymentMode, Currency, SubscriptionPlan, Company, Sale, SaleItem, Purchase, PurchaseItem,
    ExpenseCategory, Expense, Payable, Receivable, Bank, PaymentOut, PaymentIn, Report
)

class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name', 'description', 'created_at']

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'created_at']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'currency', 'currency_id', 'description', 'created_at']

class CompanySerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    subscription_plan_id = serializers.UUIDField(write_only=True, required=False)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = Company
        fields = ['id', 'name', 'subscription_plan', 'subscription_plan_id', 'payment_mode', 'payment_mode_id', 'created_at', 'updated_at']

class SaleItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = SaleItem
        fields = ['id', 'sale', 'product_id', 'quantity', 'unit_price', 'created_at']

class SaleSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    store_id = serializers.UUIDField(write_only=True)
    items = SaleItemSerializer(many=True, write_only=True)
    class Meta:
        model = Sale
        fields = ['id', 'company', 'store_id', 'customer_id', 'total_amount', 'currency', 'currency_id', 
                  'payment_mode', 'payment_mode_id', 'is_credit', 'items', 'created_at']
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)
        return sale

class PurchaseItemSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = PurchaseItem
        fields = ['id', 'purchase', 'product_id', 'quantity', 'unit_cost', 'created_at']

class PurchaseSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    store_id = serializers.UUIDField(write_only=True)
    items = PurchaseItemSerializer(many=True, write_only=True)
    class Meta:
        model = Purchase
        fields = ['id', 'company', 'store_id', 'supplier_id', 'total_amount', 'currency', 'currency_id', 
                  'payment_mode', 'payment_mode_id', 'is_credit', 'items', 'created_at']
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase = Purchase.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item_data)
        return purchase

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'company', 'name', 'description', 'created_at']

class ExpenseSerializer(serializers.ModelSerializer):
    category = ExpenseCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = Expense
        fields = ['id', 'company', 'category', 'category_id', 'amount', 'currency', 'currency_id', 
                  'payment_mode', 'payment_mode_id', 'description', 'is_credit', 'created_at']

class PayableSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    purchase_id = serializers.UUIDField(write_only=True, required=False)
    expense_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = Payable
        fields = ['id', 'company', 'type', 'purchase_id', 'expense_id', 'amount', 'currency', 'currency_id', 
                  'due_date', 'created_at']

class ReceivableSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    sale_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = Receivable
        fields = ['id', 'company', 'sale_id', 'amount', 'currency', 'currency_id', 'due_date', 'created_at']

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'company', 'account_name', 'account_number', 'bank_name', 'created_at']

class PaymentOutSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    payable_id = serializers.UUIDField(write_only=True, required=False)
    expense_id = serializers.UUIDField(write_only=True, required=False)
    bank_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = PaymentOut
        fields = ['id', 'company', 'type', 'payable_id', 'expense_id', 'amount', 'currency', 'currency_id', 
                  'payment_mode', 'payment_mode_id', 'bank_id', 'created_at']

class PaymentInSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True, required=False)
    receivable_id = serializers.UUIDField(write_only=True, required=False)
    sale_id = serializers.UUIDField(write_only=True, required=False)
    bank_id = serializers.UUIDField(write_only=True, required=False)
    class Meta:
        model = PaymentIn
        fields = ['id', 'company', 'type', 'receivable_id', 'sale_id', 'amount', 'currency', 'currency_id', 
                  'payment_mode', 'payment_mode_id', 'bank_id', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'company', 'report_type', 'data', 'generated_at']