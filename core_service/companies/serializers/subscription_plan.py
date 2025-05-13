from rest_framework import serializers
from companies.models import SubscriptionPlan

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'description',
            'price',
            'billing_cycle',
            'duration_in_months',
            'features',
            'is_active',
            'storage_limit_gb',
            'max_products',
            'max_stores',
            'max_users',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    