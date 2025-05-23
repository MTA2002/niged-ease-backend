from django.http import Http404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.models.user import User
from users.serializers.user import UserSerializer
from rest_framework.permissions import AllowAny

class UserListView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="List users",
        description="Get a list of all users",
        tags=['Users'],
        responses={
            200: UserSerializer(many=True)
        }
    )
    def get(self, request: Request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
  
    @extend_schema(
        summary="Create user",
        description="Create a new user",
        tags=['Users'],
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Bad Request")
        }
    )
    def post(self, request: Request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    def get_user(self, id):
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Get user detail",
        description="Get details of a specific user",
        tags=['Users'],
        responses={
            200: UserSerializer,
            404: OpenApiResponse(description="User not found")
        }
    )
    def get(self, request: Request, id):
        user = self.get_user(id)
        serializer = UserSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update user",
        description="Update an existing user",
        tags=['Users'],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="User not found")
        }
    )
    def put(self, request: Request, id):
        user = self.get_user(id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete user",
        description="Delete a user",
        tags=['Users'],
        responses={
            204: OpenApiResponse(description="User deleted successfully"),
            404: OpenApiResponse(description="User not found")
        }
    )
    def delete(self, request: Request, id):
        user = self.get_user(id)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)