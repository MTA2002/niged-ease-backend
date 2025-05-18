from rest_framework import serializers
from financials.models.payable import Payable


class PayableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payable
        fields = [
            'id',
            'store_id',
            'purchase',
            'amount',
            'currency',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'purchase': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the purchase belongs to the same store.
        """
        purchase = data.get('purchase')
        store_id = data.get('store_id')
        
        if purchase and store_id and purchase.store_id != store_id:
            raise serializers.ValidationError(
                "The selected purchase does not belong to this store."
            )
        
        return data 