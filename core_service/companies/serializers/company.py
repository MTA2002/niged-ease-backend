from rest_framework import serializers
from companies.models import Company, Subscription, SubscriptionPlan

class CompanySerializer(serializers.ModelSerializer):
    subscription_plan_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'is_subscribed',
            'current_subscription',
            'subscription_plan_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_subscription']

    def create(self, validated_data):
        subscription_plan_id = validated_data.pop('subscription_plan_id', None)
        
        # Create company first
        company = super().create(validated_data)
        
        # If subscription plan is provided, create a subscription
        if subscription_plan_id:
            try:
                plan = SubscriptionPlan.objects.get(id=subscription_plan_id)
                subscription = Subscription.objects.create(
                    company=company,
                    plan=plan
                )
                company.current_subscription = subscription
                company.is_subscribed = True
                company.save()
            except SubscriptionPlan.DoesNotExist:
                raise serializers.ValidationError({
                    'subscription_plan_id': 'Invalid subscription plan ID'
                })
        
        return company

