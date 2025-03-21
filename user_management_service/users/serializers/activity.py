from rest_framework import serializers
from users.models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_email', 'action', 'description', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at'] 