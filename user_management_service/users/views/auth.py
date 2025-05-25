# type: ignore
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

from users.serializers.auth import LoginSerializer, RefreshTokenSerializer, ResendOTPSerializer, VerifyOTPSerializer, VerifyTokenSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer


def create_otp_email_html(otp: str, user_name: str) -> str:
    """Create beautifully formatted HTML email for OTP"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your OTP Code</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .email-container {{
                background-color: #ffffff;
                border-radius: 10px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-top: 4px solid #4CAF50;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
            }}
            .title {{
                font-size: 24px;
                color: #2c3e50;
                margin-bottom: 20px;
            }}
            .greeting {{
                font-size: 16px;
                color: #555;
                margin-bottom: 25px;
            }}
            .otp-container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 30px;
                text-align: center;
                margin: 30px 0;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            .otp-label {{
                color: #ffffff;
                font-size: 16px;
                margin-bottom: 10px;
                font-weight: 500;
            }}
            .otp-code {{
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 8px;
                margin: 15px 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .otp-note {{
                color: #f8f9fa;
                font-size: 14px;
                margin-top: 15px;
            }}
            .instructions {{
                background-color: #f8f9fa;
                border-left: 4px solid #4CAF50;
                padding: 20px;
                margin: 25px 0;
                border-radius: 5px;
            }}
            .instructions h3 {{
                color: #2c3e50;
                margin-top: 0;
                font-size: 18px;
            }}
            .instructions ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .instructions li {{
                margin: 8px 0;
                color: #555;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #777;
                font-size: 14px;
            }}
            .support {{
                background-color: #e8f5e8;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                text-align: center;
            }}
            .support a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            @media (max-width: 600px) {{
                .email-container {{
                    padding: 20px;
                }}
                .otp-code {{
                    font-size: 28px;
                    letter-spacing: 4px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">🔐 NgedEase</div>
                <h1 class="title">Verification Code</h1>
            </div>
            
            <div class="greeting">
                Hello{f", {user_name}" if user_name else ""},
            </div>
            
            <p>We received a request to access your account. To complete the verification process, please use the One-Time Password (OTP) below:</p>
            
            <div class="otp-container">
                <div class="otp-label">Your Verification Code</div>
                <div class="otp-code">{otp}</div>
                <div class="otp-note">This code expires in 10 minutes</div>
            </div>
            
            <div class="instructions">
                <h3>📋 How to use this code:</h3>
                <ul>
                    <li>Enter this 6-digit code in the verification field</li>
                    <li>Complete the process within 10 minutes</li>
                    <li>Do not share this code with anyone</li>
                </ul>
            </div>
            
            <div class="warning">
                ⚠️ <strong>Security Notice:</strong> If you didn't request this code, please ignore this email and ensure your account is secure.
            </div>
            
            <div class="support">
                Need help? Contact our support team at <a href="mailto:mahfouzteyib57@gmail.com">mahfouzteyib57@gmail.com</a>
            </div>
            
            <div class="footer">
                <p>This is an automated message from NgedEase. Please do not reply to this email.</p>
                <p>&copy; 2025 NgedEase. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


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

        # Create beautiful HTML email
        html_message = create_otp_email_html(otp, user.first_name)

        send_mail(
            'Your NgedEase Verification Code',
            f'Your OTP verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this code, please ignore this email.',
            'mahfouz.teyib@a2sv.org',
            [user.email],
            fail_silently=False,
            html_message=html_message,
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

        # Create beautiful HTML email
        html_message = create_otp_email_html(otp, user.first_name)

        send_mail(
            'Your NgedEase Verification Code',
            f'Your OTP verification code is: {otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this code, please ignore this email.',
            'mahfouz.teyib@a2sv.org',
            [user.email],
            fail_silently=False,
            html_message=html_message,
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


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Request password reset",
        description="Send password reset OTP to email address",
        tags=['Authentication'],
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description='OTP sent successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'example': "Password reset OTP sent to your email"}
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
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate OTP
        otp = get_random_string(length=6, allowed_chars='0123456789')
        
        # Save OTP
        OTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp}
        )

        # Create HTML email for password reset
        html_message = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Request</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 40px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-top: 4px solid #e74c3c;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #e74c3c;
                    margin-bottom: 10px;
                }}
                .title {{
                    font-size: 24px;
                    color: #2c3e50;
                    margin-bottom: 20px;
                }}
                .otp-container {{
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    border-radius: 10px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                }}
                .otp-code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #ffffff;
                    letter-spacing: 8px;
                    margin: 15px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeeba;
                    color: #856404;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">🔐 NgedEase</div>
                    <h1 class="title">Password Reset Request</h1>
                </div>
                
                <p>Hello {user.first_name},</p>
                
                <p>We received a request to reset your password. Use the following code to proceed with your password reset:</p>
                
                <div class="otp-container">
                    <div class="otp-code">{otp}</div>
                </div>
                
                <p>This code will expire in 10 minutes.</p>
                
                <div class="warning">
                    If you didn't request this password reset, please ignore this email or contact support if you have concerns.
                </div>
                
                <p>Best regards,<br>The NgedEase Team</p>
            </div>
        </body>
        </html>
        """

        # Send email
        send_mail(
            'Password Reset Request',
            f'Your password reset code is: {otp}. This code will expire in 10 minutes.',
            'mahfouz.teyib@a2sv.org',
            [email],
            fail_silently=False,
            html_message=html_message
        )

        return Response(
            {"message": "Password reset OTP sent to your email"},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        summary="Confirm password reset",
        description="Reset password using OTP and new password",
        tags=['Authentication'],
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                description='Password reset successful',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'example': "Password reset successful"}
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
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        # Get user and verify OTP
        try:
            user = User.objects.get(email=email)
            otp_object = OTP.objects.get(user=user, otp=otp)
            
            if otp_object.is_expired():
                return Response(
                    {"error": "OTP has expired. Please request a new one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(new_password)
            user.save()

            # Delete the used OTP
            otp_object.delete()

            return Response(
                {"message": "Password reset successful"},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except OTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )