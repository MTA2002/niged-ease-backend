from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models.supplier import Supplier
from transactions.serializers.supplier import SupplierSerializer


class SupplierListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all suppliers",
        responses={200: SupplierSerializer(many=True)}
    )
    def get(self, request: Request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new supplier",
        request_body=SupplierSerializer,
        responses={
            201: SupplierSerializer,
            400: "Invalid data"
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
    
    @swagger_auto_schema(
        operation_description="Get a specific supplier by ID",
        responses={
            200: SupplierSerializer,
            404: "Supplier not found"
        }
    )
    def get(self, request: Request, id):
        supplier = self.get_supplier(id)
        serializer = SupplierSerializer(supplier)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a supplier",
        request_body=SupplierSerializer,
        responses={
            200: SupplierSerializer,
            400: "Invalid data",
            404: "Supplier not found"
        }
    )
    def put(self, request: Request, id):
        supplier = self.get_supplier(id)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a supplier",
        responses={
            204: "Supplier deleted successfully",
            404: "Supplier not found"
        }
    )
    def delete(self, request: Request, id):
        supplier = self.get_supplier(id)
        supplier.delete()
        return Response({'message': 'Supplier deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 