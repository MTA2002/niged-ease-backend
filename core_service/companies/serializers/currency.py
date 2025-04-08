from rest_framework import serializers

from companies.models.currency import Currency

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

