from datetime import timedelta
from django.utils import timezone  
import uuid
from django.db import models

class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def is_expired(self):
       
        return self.updated_at + timedelta(minutes=10) < timezone.now()