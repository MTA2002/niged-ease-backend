from rest_framework import serializers
from transactions.models.customer import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 
            'phone', 'address', 
            'credit_limit', 'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 