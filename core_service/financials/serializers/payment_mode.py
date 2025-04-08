from rest_framework import serializers
from financials.models.payment_mode import PaymentMode


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True}
        }

    def validate_name(self, value):
        """
        Validate that the payment mode name is unique.
        """
        if PaymentMode.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "A payment mode with this name already exists."
            )
        return value 