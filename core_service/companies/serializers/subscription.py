from rest_framework import serializers
from companies.models import Subscription
from .subscription_plan import SubscriptionPlanSerializer

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'start_date', 'end_date', 'is_active'] 