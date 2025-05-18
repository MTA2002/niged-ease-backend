from rest_framework import serializers
from financials.models.receivable import Receivable


class ReceivableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receivable
        fields = [
            'id',
            'store_id',
            'sale',
            'amount',
            'currency',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'store_id': {'required': True},
            'sale': {'required': True},
            'amount': {'required': True},
            'currency': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the sale belongs to the same store.
        """
        sale = data.get('sale')
        store_id = data.get('store_id')
        
        if sale and store_id and sale.store_id != store_id:
            raise serializers.ValidationError(
                "The selected sale does not belong to this store."
            )
        
        return data 