from rest_framework import serializers

from companies.models.subscription_plan import SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):

  class Meta:
    model = SubscriptionPlan
    fields = [
          'id', 'name', 'description',
          'price','billing_cycle','features','is_active','storage_limit_gb', 'created_at', 'updated_at'
    ]

    