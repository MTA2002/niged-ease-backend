from rest_framework import serializers
from companies.models.company import Company
from companies.serializers.currency import CurrencySerializer
from companies.serializers.subscription_plan import SubscriptionPlanSerializer

class CompanySerializer(serializers.ModelSerializer):
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    subscription_plan_id = serializers.UUIDField(write_only=True)
    currency_id = serializers.UUIDField(write_only=True)
    

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'short_name', 'address',
            'subscription_plan', 'currency',
            'subscription_plan_id', 'currency_id',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['subscription_plan_id'] = validated_data.pop('subscription_plan_id')
        validated_data['currency_id'] = validated_data.pop('currency_id')
        return super().create(validated_data)