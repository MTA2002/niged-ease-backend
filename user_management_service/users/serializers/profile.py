from rest_framework import serializers
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'company_id', 'email', 'first_name',
            'last_name', 'role', 'phone_number', 'profile_image',
            'assigned_store', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'company_id', 'email', 'role',
                            'assigned_store', 'created_at', 'updated_at']
