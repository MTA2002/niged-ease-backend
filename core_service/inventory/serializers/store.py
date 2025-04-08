from rest_framework import serializers
from inventory.models.store import Store
from companies.serializers.company import CompanySerializer

class StoreSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = [
            'id', 'company', 'name', 
            'location', 'created_at', 
            'updated_at'
        ] 