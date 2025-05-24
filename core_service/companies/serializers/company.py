from rest_framework import serializers
from companies.models import Company

class CompanySerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'is_subscribed',
            'subscription_plan',
            'currency',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'subscription_plan': {'required': False, 'allow_null': True}
        }
    
    def get_is_subscribed(self, obj):
        return obj.is_subscription_valid()

