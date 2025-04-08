from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.product_unit import ProductUnit
from inventory.serializers.product_unit import ProductUnitSerializer


class ProductUnitListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all product units",
        responses={200: ProductUnitSerializer(many=True)}
    )
    def get(self, request: Request):
        units = ProductUnit.objects.all()
        serializer = ProductUnitSerializer(units, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new product unit",
        request_body=ProductUnitSerializer,
        responses={
            201: ProductUnitSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = ProductUnitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductUnitDetailView(APIView):
    def get_unit(self, id):
        try:
            unit = ProductUnit.objects.get(pk=id)
            return unit
        except ProductUnit.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific product unit by ID",
        responses={
            200: ProductUnitSerializer,
            404: "Product unit not found"
        }
    )
    def get(self, request: Request, id):
        unit = self.get_unit(id)
        serializer = ProductUnitSerializer(unit)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a product unit",
        request_body=ProductUnitSerializer,
        responses={
            200: ProductUnitSerializer,
            400: "Invalid data",
            404: "Product unit not found"
        }
    )
    def put(self, request: Request, id):
        unit = self.get_unit(id)
        serializer = ProductUnitSerializer(unit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a product unit",
        responses={
            204: "Product unit deleted successfully",
            404: "Product unit not found"
        }
    )
    def delete(self, request: Request, id):
        unit = self.get_unit(id)
        unit.delete()
        return Response({'message': 'Product unit deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 