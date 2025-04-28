from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from inventory.models.product_unit import ProductUnit
from inventory.serializers.product_unit import ProductUnitSerializer


class ProductUnitListView(APIView):
    @extend_schema(
        description="Get a list of all product units",
        responses={200: ProductUnitSerializer(many=True)}
    )
    def get(self, request: Request):
        units = ProductUnit.objects.all()
        serializer = ProductUnitSerializer(units, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new product unit",
        request=ProductUnitSerializer,
        responses={
            201: ProductUnitSerializer,
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific product unit by ID",
        responses={
            200: ProductUnitSerializer,
            404: OpenApiResponse(description="Product unit not found")
        }
    )
    def get(self, request: Request, id):
        unit = self.get_unit(id)
        serializer = ProductUnitSerializer(unit)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a product unit",
        request=ProductUnitSerializer,
        responses={
            200: ProductUnitSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Product unit not found")
        }
    )
    def put(self, request: Request, id):
        unit = self.get_unit(id)
        serializer = ProductUnitSerializer(unit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a product unit",
        responses={
            204: OpenApiResponse(description="Product unit deleted successfully"),
            404: OpenApiResponse(description="Product unit not found")
        }
    )
    def delete(self, request: Request, id):
        unit = self.get_unit(id)
        unit.delete()
        return Response({'message': 'Product unit deleted successfully'}, status=status.HTTP_204_NO_CONTENT)