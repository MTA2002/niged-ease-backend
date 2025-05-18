# type: ignore
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
        description="Get a list of all suppliers for a specific store",
        responses={200: SupplierSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        suppliers = Supplier.objects.filter(store_id=store_id)
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new supplier for a specific store",
        request=SupplierSerializer,
        responses={
            201: SupplierSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        request.data['store_id'] = store_id
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailView(APIView):
    def get_supplier(self, id, store_id):
        try:
            supplier = Supplier.objects.get(pk=id, store_id=store_id)
            return supplier
        except Supplier.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific supplier by ID for a specific store",
        responses={
            200: SupplierSerializer,
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def get(self, request: Request, id, store_id):
        supplier = self.get_supplier(id, store_id)
        serializer = SupplierSerializer(supplier)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a supplier for a specific store",
        request=SupplierSerializer,
        responses={
            200: SupplierSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def put(self, request: Request, id, store_id):
        supplier = self.get_supplier(id, store_id)
        request.data['store_id'] = store_id
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a supplier for a specific store",
        responses={
            204: OpenApiResponse(description="Supplier deleted successfully"),
            404: OpenApiResponse(description="Supplier not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        supplier = self.get_supplier(id, store_id)
        supplier.delete()
        return Response({'message': 'Supplier deleted successfully'}, status=status.HTTP_204_NO_CONTENT)