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

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        return attrs
    
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        if not email or not otp:
            raise serializers.ValidationError("Email and OTP are required.")
        
        return attrs

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not OTP.objects.filter(user__email=value).exists():
            raise serializers.ValidationError("No OTP found for this email.")
        return value

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    
    def validate(self, attrs):
        refresh_token = attrs.get('refresh')
        
        if not refresh_token:
            raise serializers.ValidationError("Refresh token is required.")
        
        return attrs

class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate(self, attrs):
        token = attrs.get('token')
        
        if not token:
            raise serializers.ValidationError("Token is required.")
        
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        from users.models import User
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs