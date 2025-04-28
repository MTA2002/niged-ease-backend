from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from transactions.models.supplier import Supplier
from transactions.serializers.supplier import SupplierSerializer


class SupplierListView(APIView):
    @extend_schema(
        description="Get a list of all suppliers",
        responses={200: SupplierSerializer(many=True)}
    )
    def get(self, request: Request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new supplier",
        request=SupplierSerializer,
        responses={
            201: SupplierSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailView(APIView):
    def get_supplier(self, id):
        try:
            supplier = Supplier.objects.get(pk=id)
            return supplier
        except Supplier.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific supplier by ID",
        responses={
            200: SupplierSerializer,
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def get(self, request: Request, id):
        supplier = self.get_supplier(id)
        serializer = SupplierSerializer(supplier)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a supplier",
        request=SupplierSerializer,
        responses={
            200: SupplierSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def put(self, request: Request, id):
        supplier = self.get_supplier(id)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a supplier",
        responses={
            204: OpenApiResponse(description="Supplier deleted successfully"),
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def delete(self, request: Request, id):
        supplier = self.get_supplier(id)
        supplier.delete()
        return Response({'message': 'Supplier deleted successfully'}, status=status.HTTP_204_NO_CONTENT)