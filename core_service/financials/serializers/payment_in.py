from rest_framework import serializers
from financials.models.payment_in import PaymentIn
from transactions.serializers.payment_mode import PaymentModeSerializer


class PaymentInSerializer(serializers.ModelSerializer):
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PaymentIn
        fields = [
            'id',
            'company',
            'receivable',
            'sale',
            'amount',
            'currency',
            'payment_mode',
            'payment_mode_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'company': {'required': True},
            'receivable': {'required': True},
            'sale': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the receivable and sale belong to the same company.
        """
        receivable = data.get('receivable')
        sale = data.get('sale')
        company = data.get('company')
        
        if receivable and company and receivable.company != company:
            raise serializers.ValidationError(
                "The selected receivable does not belong to this company."
            )
            
        if sale and company and sale.company != company:
            raise serializers.ValidationError(
                "The selected sale does not belong to this company."
            )
        
        return data 