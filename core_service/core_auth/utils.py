# core_service/core/utils.py
from django.contrib.auth.models import AnonymousUser

class StatelessUser(AnonymousUser):
    def __init__(self, user_data):
        self.email = user_data.get('email', '')
        self.first_name = user_data.get('first_name', '')
        self.last_name = user_data.get('last_name', '')
        self.role = user_data.get('role', '')
        self.company_id = user_data.get('company_id', '')
        self.is_active = user_data.get('is_active', True)

    @property
    def is_authenticated(self):
        return True
    
    def __str__(self):
        return self.email