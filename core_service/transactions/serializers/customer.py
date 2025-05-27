from rest_framework import serializers
from transactions.models.customer import Customer
from inventory.serializers.store import StoreSerializer


class CustomerSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Customer
        fields = [
            'id', 'store_id', 'name', 'email', 
            'phone', 'address', 
             'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 
    
    def validate(self, data):
        return super().validate(data)