from rest_framework import serializers
from clothings.models.season import Season

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id',
            'store_id',
            'name',
            'start_date',
            'end_date',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

        extra_kwargs = {
            'store_id': {'required': True},
            'name': {'required': True},
            'start_date': {'required': True},
            'end_date': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the start date is before the end date.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "Start date must be before end date."
            )
        return data