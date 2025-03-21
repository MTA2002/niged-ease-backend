from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, Any, cast
from django.http import QueryDict
from users.models.user import User
from users.models.auth import OTP
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, Token, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Login with email and password",
        operation_description="Login with email and password to receive OTP",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email address"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="User's password",
                    min_length=8
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='OTP sent successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="OTP sent to your email"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid credentials"
                        )
                    }
                )
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

    @swagger_auto_schema(
        operation_summary="Verify OTP",
        operation_description="Verify OTP and get access token",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email address"
                ),
                'otp': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="6-digit OTP code",
                    min_length=6,
                    max_length=6,
                    pattern='^[0-9]{6}$'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='Token generated successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid OTP"
                        )
                    }
                )
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

        return Response({
            'access': access_token,
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Resend OTP",
        operation_description="Resend OTP to email address",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="User's email address"
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='OTP sent successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="OTP sent to your email"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="User not found"
                        )
                    }
                )
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

    @swagger_auto_schema(
        operation_summary="Refresh token",
        operation_description="Get new access token using refresh token",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh_token'],
            properties={
                'refresh_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JWT refresh token",
                    example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='Token refreshed successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid refresh token"
                        )
                    }
                )
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

    @swagger_auto_schema(
        operation_summary="Verify token",
        operation_description="Verify if a JWT token is valid and not blacklisted",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['token'],
            properties={
                'token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JWT token to verify",
                    example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description='Token is valid',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'is_valid': openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            example=True
                        ),
                        'user_id': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_UUID,
                            example="123e4567-e89b-12d3-a456-426614174000"
                        ),
                        'email': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_EMAIL,
                            example="user@example.com"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Invalid token',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Token is invalid or expired"
                        )
                    }
                )
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
                'email': user.email
            }, status=status.HTTP_200_OK)

        except (InvalidToken, TokenError, User.DoesNotExist):
            return Response(
                {"error": "Token is invalid or expired"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    