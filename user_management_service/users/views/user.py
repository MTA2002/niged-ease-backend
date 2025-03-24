from rest_framework.views import APIView
from users.models.user import User
from users.serializers.user import UserSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserListView(APIView):

  @swagger_auto_schema(
      operation_summary="List users",
      operation_description="Get a list of all users",
      tags=['Users'], 
      responses={
          200: UserSerializer(many=True)
      }
  )
  def get(self, request: Request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema( 
      operation_summary="Create user",
      operation_description="Create a new user",
      tags=['Users'],
      request_body=UserSerializer,
      responses={
          201: UserSerializer,
          400: 'Bad Request'
      }
  )


  def post(self, request: Request):
    print(request.data,11)
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):

  @swagger_auto_schema(
      operation_summary="Get user detail",
      operation_description="Get details of a specific user",
      tags=['Users'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="User ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      responses={
          200: UserSerializer,
          404: 'Not Found'
      }
  )
  def get(self, request: Request, id):
    try:
      user = User.objects.get(pk = id)
      serializer = UserSerializer(user)
      return Response(data=serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
       return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

  @swagger_auto_schema(
      operation_summary="Update user",
      operation_description="Update an existing user",
      tags=['Users'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="User ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      request_body=UserSerializer,
      responses={
          200: UserSerializer,
          400: 'Bad Request',
          404: 'Not Found'
      }
  )
  def put(self, request:Request, id):
    try:
      user = User.objects.get(pk = id)
      serializer = UserSerializer(user, data = request.data)
      if serializer.is_valid():
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
      return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

  @swagger_auto_schema(
      operation_summary="Delete user",
      operation_description="Delete a user",
      tags=['Users'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="User ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      responses={
          204: 'No Content',
          404: 'Not Found'
      }
  )
  def delete(self, request:Request, id):
    try:
      user = User.objects.get(pk = id)
      user.delete()
      return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
      return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)