from rest_framework import serializers
from companies.models.store import Store
from companies.serializers.company import CompanySerializer
from companies.models.company import Company

class StoreSerializer(serializers.ModelSerializer):
    company_id = serializers.UUIDField(write_only=True)
    company = CompanySerializer(read_only=True)
    
    class Meta:
        model = Store
        fields = [
            'id', 'company_id', 'company', 'name', 
            'location', 'created_at', 
            'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company_id': {'required': True},
            'name': {'required': True},
            'location': {'required': True},
            'is_active': {'required': False}
        }

    def create(self, validated_data):
        company_id = validated_data.pop('company_id')
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Invalid company ID")
        
        return Store.objects.create(company_id=company, **validated_data) 