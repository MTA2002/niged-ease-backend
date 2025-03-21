from rest_framework import serializers
from users.models import OTP

class OTPSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = OTP
        fields = ['id', 'user', 'user_email', 'otp', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'otp': {'write_only': True}  # Hide OTP in responses for security
        } 