from django.http import Http404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from users.models.role import Permission, Role
from users.serializers.role import PermissionSerializer, RoleSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all roles",
        operation_description="Returns a list of all roles with their associated permissions",
        responses={
            200: RoleSerializer(many=True),
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new role",
        operation_description="Create a new role with optional permissions",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_role(self, id):
        try:
            return Role.objects.get(id=id)
        except Role.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Get role details",
        operation_description="Returns details of a specific role including its permissions",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Role ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            200: RoleSerializer,
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def get(self, request, id):
        role = self.get_role(id)
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a role",
        operation_description="Update a role's details and/or permissions",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Role ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: "Bad Request",
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def put(self, request, id):
        role = self.get_role(id)
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a role",
        operation_description="Delete a role and its permission associations",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Role ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            204: "No Content",
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def delete(self, request, id):
        role = self.get_role(id)
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all permissions",
        operation_description="Returns a list of all available permissions",
        responses={
            200: PermissionSerializer(many=True),
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new permission",
        operation_description="Create a new permission that can be assigned to roles",
        request_body=PermissionSerializer,
        responses={
            201: PermissionSerializer,
            400: "Bad Request",
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def post(self, request):
        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            permission = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permission(self, id):
        try:
            return Permission.objects.get(id=id)
        except Permission.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Get permission details",
        operation_description="Returns details of a specific permission",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Permission ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            200: PermissionSerializer,
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def get(self, request, id):
        permission = self.get_permission(id)
        if not permission:
            return Response({"detail": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PermissionSerializer(permission)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a permission",
        operation_description="Update a permission's details",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Permission ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        request_body=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: "Bad Request",
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def put(self, request, id):
        permission = self.get_permission(id)
        if not permission:
            return Response({"detail": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PermissionSerializer(permission, data=request.data)
        if serializer.is_valid():
            permission = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a permission",
        operation_description="Delete a permission and remove it from all roles",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="Permission ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            )
        ],
        responses={
            204: "No Content",
            404: "Not Found",
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def delete(self, request, id):
        permission = self.get_permission(id)
        if not permission:
            return Response({"detail": "Permission not found"}, status=status.HTTP_404_NOT_FOUND)
        permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)