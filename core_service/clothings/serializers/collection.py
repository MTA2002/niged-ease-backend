from rest_framework import serializers
from clothings.models.collection import Collection
from clothings.models.season import Season
from clothings.serializers.season import SeasonSerializer
from companies.serializers.store import StoreSerializer
from companies.models.store import Store


class CollectionSerializer(serializers.ModelSerializer):
    # Add method fields for store and season details
    store = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'id',
            'store_id',
            'season_id',
            'name',
            'release_date',
            'description',
            'store',
            'season',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'store', 'season']
        write_only_fields = ['store_id', 'season_id']
        extra_kwargs = {
            'store_id': {'required': True},
            'season_id': {'required': True},
            'name': {'required': True},
            'release_date': {'required': True}
        }

    def get_store(self, obj):
        """Get the store details"""
        store = Store.objects.get(id=obj.store_id.id)
        return StoreSerializer(store).data

    def get_season(self, obj):
        """Get the season details"""
        season = Season.objects.get(id=obj.season_id.id)
        return SeasonSerializer(season).data

    def validate(self, data):
        """
        Validate that the season belongs to the same store.
        """
        print('data', data.get('season_id').name)
        season = data.get('season_id')
        store = data.get('store_id')
        print('season', season.store_id.id)
        print('store', store.id)
        if season and store and season.store_id.id != store.id:
            raise serializers.ValidationError(
                "The selected season does not belong to this store."
            )
        return data
    
    def create(self, validated_data):
        print('validated_data', validated_data)
        return super().create(validated_data)

        