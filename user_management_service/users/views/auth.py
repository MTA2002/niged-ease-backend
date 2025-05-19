import os
import requests
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, Any, cast
from users.models.user import User
from users.models.auth import OTP
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import check_password
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from users.serializers.auth import LoginSerializer, RefreshTokenSerializer, ResendOTPSerializer, VerifyOTPSerializer, VerifyTokenSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Login with email and password",
        description="Login with email and password to receive OTP",
        tags=['Authentication'],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description='OTP sent successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'example': "OTP sent to your email"}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Bad Request',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string', 'example': "Invalid credentials"}
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        data = cast(Dict[str, Any], request.data)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({"error": "Both email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        otp = get_random_string(length=6, allowed_chars='0123456789')
          
        OTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}',
            'mahfouz.teyib@a2sv.org',
            [user.email],
            fail_silently=False,
        )
        
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Verify OTP",
        description="Verify OTP and get access token",
        tags=['Authentication'],
        request=VerifyOTPSerializer,
        responses={
            200: OpenApiResponse(
                description='Token generated successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string', 'example': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        'refresh': {'type': 'string', 'example': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Bad Request',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string', 'example': "Invalid OTP"}
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        data = cast(Dict[str, Any], request.data)
        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return Response({"error": "Both email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_object = OTP.objects.filter(user=user, otp=otp).first()

        if not otp_object:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_object.is_expired():
            return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        if user.role == 'stock_manager' or user.role == 'sales':
            core_service_url = os.getenv('CORE_SERVICE_URL', 'http://localhost:8000')
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(f'{core_service_url}/companies/companies/{user.company_id}/stores/{user.assigned_store}/', headers=headers)
            if response.status_code != 200:
                stores = None
            
            stores = response.json()
        else:
            core_service_url = os.getenv('CORE_SERVICE_URL', 'http://localhost:8000')
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.get(f'{core_service_url}/companies/companies/{user.company_id}/stores/', headers=headers)
            stores = response.json()

        return Response({
            'access': access_token,
            'refresh': str(refresh),
            'role' : user.role,
            'company_id' : user.company_id if user.company_id else '',
            'stores' : stores
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Resend OTP",
        description="Resend OTP to email address",
        tags=['Authentication'],
        request=ResendOTPSerializer,
        responses={
            200: OpenApiResponse(
                description='OTP sent successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'example': "OTP sent to your email"}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Bad Request',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string', 'example': "User not found"}
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        data = cast(Dict[str, Any], request.data)
        email = data.get('email')

        if not email:
            return Response({"error": "Email must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        otp = get_random_string(length=6, allowed_chars='0123456789')
          
        OTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        send_mail(
            'Your OTP Code',
            f'Your OTP is {otp}',
            'mahfouz.teyib@a2sv.org',
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Refresh token",
        description="Get new access token using refresh token",
        tags=['Authentication'],
        request=RefreshTokenSerializer,
        responses={
            200: OpenApiResponse(
                description='Token refreshed successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string', 'example': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."},
                        'refresh': {'type': 'string', 'example': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Bad Request',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string', 'example': "Invalid refresh token"}
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        data = cast(Dict[str, Any], request.data)
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return Response({"error": "Refresh token must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        
        except InvalidToken:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

        except TokenError:
            return Response({"error": "Error occurred with the refresh token"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Verify token",
        description="Verify if a JWT token is valid and not blacklisted",
        tags=['Authentication'],
        request=VerifyTokenSerializer,
        responses={
            200: OpenApiResponse(
                description='Token is valid',
                response={
                    'type': 'object',
                    'properties': {
                        'is_valid': {'type': 'boolean', 'example': True},
                        'user_id': {'type': 'string', 'format': 'uuid', 'example': "123e4567-e89b-12d3-a456-426614174000"},
                        'email': {'type': 'string', 'format': 'email', 'example': "user@example.com"}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid token',
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string', 'example': "Token is invalid or expired"}
                    }
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        data = cast(Dict[str, Any], request.data)
        token = data.get('token')

        if not token:
            return Response(
                {"error": "Token must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            user = User.objects.get(id=user_id)
            

            return Response({
                'is_valid': True,
                'user_id': str(user.id),
                'email': user.email,
                'role' : user.role,
            }, status=status.HTTP_200_OK)

        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response(
                {"error": "Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST
            )