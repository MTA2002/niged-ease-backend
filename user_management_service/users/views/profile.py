from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.serializers.profile import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get user profile",
        description="Get the profile of the currently authenticated user",
        tags=['Profile'],
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided")
        }
    )
    def get(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update user profile",
        description="Update the profile of the currently authenticated user",
        tags=['Profile'],
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Authentication credentials were not provided")
        }
    )
    def put(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the profile of the currently authenticated user",
        tags=['Profile'],
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Authentication credentials were not provided")
        }
    )
    def patch(self, request: Request) -> Response:
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
