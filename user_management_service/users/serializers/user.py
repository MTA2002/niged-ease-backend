from rest_framework import serializers
from users.models import User, Role

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, 
                                   style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'company_id', 'email', 'password', 'first_name', 
                 'last_name', 'role', 'profile_image', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance 