from rest_framework import serializers
from financials.models.receivable import Receivable


class ReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receivable
        fields = [
            'id',
            'company',
            'sale',
            'amount',
            'currency',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company': {'required': True},
            'sale': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the sale belongs to the same company.
        """
        sale = data.get('sale')
        company = data.get('company')
        
        if sale and company and sale.company != company:
            raise serializers.ValidationError(
                "The selected sale does not belong to this company."
            )
        
        return data 