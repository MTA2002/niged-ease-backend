from rest_framework import serializers
from financials.models.payment_out import PaymentOut
from transactions.serializers.payment_mode import PaymentModeSerializer


class PaymentOutSerializer(serializers.ModelSerializer):
    payment_mode = PaymentModeSerializer(read_only=True)
    payment_mode_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PaymentOut
        fields = [
            'id',
            'company',
            'payable',
            'purchase',
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
            'payable': {'required': True},
            'purchase': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the payable and purchase belong to the same company.
        """
        payable = data.get('payable')
        purchase = data.get('purchase')
        company = data.get('company')
        
        if payable and company and payable.company != company:
            raise serializers.ValidationError(
                "The selected payable does not belong to this company."
            )
            
        if purchase and company and purchase.company != company:
            raise serializers.ValidationError(
                "The selected purchase does not belong to this company."
            )
        
        return data 