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
        print('mahfouz')
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        logger.info(f"Authentication attempt - Authorization header present: {bool(auth_header)}")

        if not auth_header:
            logger.warning("No Authorization header found in request")
            return None
        
        # Handle both "Bearer token" and "Bearer Bearer token" formats
        parts = auth_header.split()
        
        if len(parts) == 2:
            token = parts[1]
        elif len(parts) == 3 and parts[0] == 'Bearer' and parts[1] == 'Bearer':
            token = parts[2]
        else:
            logger.warning(f"Invalid Authorization header format: {auth_header}")
            return None
            
        logger.info("Token successfully extracted from header")
        
        try:
            # First try to decode the token to get user_id
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            logger.info(f"Decoded token payload: {decoded_token}")
            
            user_id = decoded_token.get('user_id')
            if not user_id:
                logger.error("No user_id found in token")
                raise exceptions.AuthenticationFailed('Invalid token: no user_id')

            # Create basic user data from token
            user_data = {
                'id': user_id,
                'is_active': True
            }
            
            # Get User Service URL from environment
            user_service_url = os.getenv('USER_SERVICE_URL')
            logger.info(f"Using USER_SERVICE_URL: {user_service_url}")
            
            if user_service_url:
                verify_url = f"{user_service_url.rstrip('/')}/auth/verify-token/"
                headers = {'Authorization': f'Bearer {token}'}
                
                try:
                    logger.info(f"Making verification request to: {verify_url}")
                    response = requests.post(
                        verify_url, 
                        headers=headers, 
                        timeout=30,
                        json={'token': token},
                        verify=False
                    )
                    
                    if response.ok:
                        data = response.json()
                        if data.get('is_valid'):
                            # Update user data with additional info from user service
                            user_info = data
                            if user_info:
                                user_data.update(user_info)
                except Exception as e:
                    logger.warning(f"Failed to get additional user info from user service: {str(e)}")
                    # Continue with basic user data since we have the user_id from token
            
            user = StatelessUser(user_data=user_data)
            logger.info(f"Successfully created StatelessUser with ID: {user.id}")
            return (user, token)
            
        except jwt.DecodeError as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise exceptions.AuthenticationFailed('Invalid token format')
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise exceptions.AuthenticationFailed('Authentication failed')