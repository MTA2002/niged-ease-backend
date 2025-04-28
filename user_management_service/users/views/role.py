from django.http import Http404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.models.role import Permission, Role
from users.serializers.role import PermissionSerializer, RoleSerializer


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all roles",
        description="Returns a list of all roles with their associated permissions",
        tags=['Roles'],
        responses={
            200: RoleSerializer(many=True),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def get(self, request: Request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new role",
        description="Create a new role with optional permissions",
        tags=['Roles'],
        request=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def post(self, request: Request):
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
            raise Http404

    @extend_schema(
        summary="Get role details",
        description="Returns details of a specific role including its permissions",
        tags=['Roles'],
        responses={
            200: RoleSerializer,
            404: OpenApiResponse(description="Role not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def get(self, request: Request, id):
        role = self.get_role(id)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a role",
        description="Update a role's details and/or permissions",
        tags=['Roles'],
        request=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Role not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def put(self, request: Request, id):
        role = self.get_role(id)
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a role",
        description="Delete a role and its permission associations",
        tags=['Roles'],
        responses={
            204: OpenApiResponse(description="Role deleted successfully"),
            404: OpenApiResponse(description="Role not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def delete(self, request: Request, id):
        role = self.get_role(id)
        role.delete()
        return Response({'message': 'Role deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all permissions",
        description="Returns a list of all available permissions",
        tags=['Permissions'],
        responses={
            200: PermissionSerializer(many=True),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def get(self, request: Request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a new permission",
        description="Create a new permission that can be assigned to roles",
        tags=['Permissions'],
        request=PermissionSerializer,
        responses={
            201: PermissionSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def post(self, request: Request):
        serializer = PermissionSerializer(data=request.data)
        if serializer.is_valid():
            permission = serializer.save()
            return Response(PermissionSerializer(permission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permission(self, id):
        try:
            return Permission.objects.get(id=id)
        except Permission.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="Get permission details",
        description="Returns details of a specific permission",
        tags=['Permissions'],
        responses={
            200: PermissionSerializer,
            404: OpenApiResponse(description="Permission not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def get(self, request: Request, id):
        permission = self.get_permission(id)
        serializer = PermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a permission",
        description="Update a permission's details",
        tags=['Permissions'],
        request=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Permission not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def put(self, request: Request, id):
        permission = self.get_permission(id)
        serializer = PermissionSerializer(permission, data=request.data)
        if serializer.is_valid():
            permission = serializer.save()
            return Response(PermissionSerializer(permission).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a permission",
        description="Delete a permission and remove it from all roles",
        tags=['Permissions'],
        responses={
            204: OpenApiResponse(description="Permission deleted successfully"),
            404: OpenApiResponse(description="Permission not found"),
            401: OpenApiResponse(description="Unauthorized")
        }
    )
    def delete(self, request: Request, id):
        permission = self.get_permission(id)
        permission.delete()
        return Response({'message': 'Permission deleted successfully'}, status=status.HTTP_204_NO_CONTENT)