from rest_framework import serializers
from clothings.models.color import Color

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = [
            'id',
            'name',
            'color_code',
            'created_at',
            'updated_at',
            'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

        extra_kwargs = {
            'name': {'required': True},
            'color_code': {'required': True}
        }

    def validate(self, data):
        """
        Validate that the color code is in the correct format.
        """
        color_code = data.get('color_code')
        if not color_code.startswith('#') or len(color_code) != 7:
            raise serializers.ValidationError(
                "Color code must be in the format '#RRGGBB'."
            )
        return data