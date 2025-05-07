# core_service/core_service/authentication.py
import requests
from rest_framework import authentication, exceptions
from core_auth.utils import StatelessUser  # Import from core app
import os

class UserServiceAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        print(f"Authorization header: {auth_header}")
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No token, let other auth methods handle or raise 401
          # Debugging line
        token = auth_header.split(' ')[1]
        print(f"Token received: {token}")  # Debugging line
        user_service_url = os.getenv('USER_SERVICE_URL', 'http://127.0.0.1:8001') + '/auth/verify-token/'
        # Call User Service's verify token endpoint
        print(f"User Service URL: {os.getenv('USER_SERVICE_URL')}")
        print(f"User Service URL: {user_service_url}")
        headers = {'Authorization': f'Bearer {token}'}
        try:
            print(f"Making request to User Service with headers: {headers}")  # Debugging line
            response = requests.post(user_service_url, headers=headers, timeout=5, json={'token': token})            # response.raise_for_status()  # Raise for 4xx/5xx errors
            data = response.json()
            print(f"Response from User Service: {data}")  # Debugging line
        except requests.RequestException as e:
            raise exceptions.AuthenticationFailed(f'User Service error: {str(e)}')

        # Validate response
        is_valid = data.get('is_valid', False)
        if not is_valid:
            raise exceptions.AuthenticationFailed(data.get('message', 'Invalid or expired token'))

        # Create stateless user
        print(f"Creating StatelessUser with data: {data}")
        user = StatelessUser(
            user_data={
                'email': 'email@email.com',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'role': 'role',
                'company_id': data.get('company_id'),
                'is_active': 'is_active'
            }
        )
        print(f"StatelessUser created: {user}")

        return (user, token)  # Return (user, token) tuple