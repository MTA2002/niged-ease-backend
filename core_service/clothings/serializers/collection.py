
from rest_framework import serializers
from clothings.models.collection import Collection


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = [
            'id',
            'company_id',
            'season_id',
            'name',
            'release_date',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

        extra_kwargs = {
            'company_id': {'required': True},
            'season_id': {'required': True},
            'name': {'required': True},
            'release_date': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the season belongs to the same company.
        """
        season = data.get('season_id')
        company = data.get('company_id')
        if season and company and season.company_id != company:
            raise serializers.ValidationError(
                "The selected season does not belong to this company."
            )
        return data
    

        