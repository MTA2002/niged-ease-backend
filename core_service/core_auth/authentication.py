# core_service/core_service/authentication.py
import requests
from rest_framework import authentication, exceptions
from core_auth.utils import StatelessUser
import os
import json
import logging
import jwt
from django.conf import settings

logger = logging.getLogger(__name__)

class UserServiceAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        logger.debug(f"Authorization header: {auth_header}")
        
        if not auth_header:
            logger.debug("No Authorization header found")
            return None
            
        # Handle both "Bearer token" and "Bearer Bearer token" formats
        parts = auth_header.split()
        if len(parts) == 2:
            token = parts[1]
        elif len(parts) == 3 and parts[0] == 'Bearer' and parts[1] == 'Bearer':
            token = parts[2]
        else:
            logger.debug("Invalid Authorization header format")
            return None
            
        logger.debug(f"Token received: {token}")
        
        # Get User Service URL from environment
        user_service_url = os.getenv('USER_SERVICE_URL')
        logger.debug(f"USER_SERVICE_URL from env: {user_service_url}")
        
        if not user_service_url:
            logger.error("USER_SERVICE_URL not configured")
            raise exceptions.AuthenticationFailed('Authentication service not configured')
            
        verify_url = f"{user_service_url.rstrip('/')}/auth/verify-token/"
        logger.debug(f"Verification URL: {verify_url}")
        
        headers = {'Authorization': f'Bearer {token}'}
        try:
            logger.debug(f"Making request to User Service with headers: {headers}")
            response = requests.post(
                verify_url, 
                headers=headers, 
                timeout=30,  # Increased timeout to 30 seconds
                json={'token': token},
                verify=False  # Disable SSL verification for local development
            )
            
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
            
            # Check if response is valid JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response from User Service: {response.text}")
                raise exceptions.AuthenticationFailed('Invalid response from authentication service')
                
            logger.debug(f"Response from User Service: {data}")
            
            # Validate response
            if not response.ok:
                error_message = data.get('detail', 'Authentication failed')
                logger.error(f"User Service error: {error_message}")
                raise exceptions.AuthenticationFailed(error_message)
                
            # Check if token is valid
            is_valid = data.get('is_valid', False)
            if not is_valid:
                error_message = data.get('message', 'Invalid or expired token')
                logger.error(f"Invalid token: {error_message}")
                raise exceptions.AuthenticationFailed(error_message)

            # Create stateless user from response data
            user_data = data.get('user', {})
            if not user_data:
                # If no user data in response, try to create user from token data
                try:
                    # Try to decode without verification first to get the payload
                    decoded_token = jwt.decode(token, options={"verify_signature": False})
                    logger.debug(f"Decoded token payload: {decoded_token}")
                    
                    # Create user data from token payload
                    user_data = {
                        'id': decoded_token.get('user_id'),
                        'username': decoded_token.get('username', ''),
                        'email': decoded_token.get('email', ''),
                        'is_active': True
                    }
                    logger.debug(f"Created user data from token: {user_data}")
                except Exception as e:
                    logger.error(f"Failed to decode token: {str(e)}")
                    raise exceptions.AuthenticationFailed('No user data received and token decode failed')

            if not user_data:
                logger.error("No user data in response and could not create from token")
                raise exceptions.AuthenticationFailed('No user data received')
                
            user = StatelessUser(user_data=user_data)
            logger.debug(f"StatelessUser created: {user}")

            return (user, token)  # Return (user, token) tuple
            
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to User Service")
            raise exceptions.AuthenticationFailed('Could not connect to authentication service - please ensure it is running')
        except requests.exceptions.Timeout:
            logger.error("Request to User Service timed out")
            raise exceptions.AuthenticationFailed('Authentication service timeout - please try again')
        except requests.exceptions.SSLError:
            logger.error("SSL error when connecting to User Service")
            raise exceptions.AuthenticationFailed('SSL error when connecting to authentication service')
        except requests.RequestException as e:
            logger.error(f"Request to User Service failed: {str(e)}")
            raise exceptions.AuthenticationFailed(f'Authentication service error: {str(e)}')
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise exceptions.AuthenticationFailed('Authentication failed')