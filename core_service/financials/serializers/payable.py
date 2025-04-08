from rest_framework import serializers
from financials.models.payable import Payable


class PayableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payable
        fields = [
            'id',
            'company',
            'purchase',
            'amount',
            'currency',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company': {'required': True},
            'purchase': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the purchase belongs to the same company.
        """
        purchase = data.get('purchase')
        company = data.get('company')
        
        if purchase and company and purchase.company != company:
            raise serializers.ValidationError(
                "The selected purchase does not belong to this company."
            )
        
        return data 