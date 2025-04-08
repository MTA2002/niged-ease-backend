from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.product_category import ProductCategory
from inventory.serializers.product_category import ProductCategorySerializer


class ProductCategoryListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all product categories",
        responses={200: ProductCategorySerializer(many=True)}
    )
    def get(self, request: Request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new product category",
        request_body=ProductCategorySerializer,
        responses={
            201: ProductCategorySerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryDetailView(APIView):
    def get_category(self, id):
        try:
            category = ProductCategory.objects.get(pk=id)
            return category
        except ProductCategory.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific product category by ID",
        responses={
            200: ProductCategorySerializer,
            404: "Product category not found"
        }
    )
    def get(self, request: Request, id):
        category = self.get_category(id)
        serializer = ProductCategorySerializer(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a product category",
        request_body=ProductCategorySerializer,
        responses={
            200: ProductCategorySerializer,
            400: "Invalid data",
            404: "Product category not found"
        }
    )
    def put(self, request: Request, id):
        category = self.get_category(id)
        serializer = ProductCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a product category",
        responses={
            204: "Product category deleted successfully",
            404: "Product category not found"
        }
    )
    def delete(self, request: Request, id):
        category = self.get_category(id)
        category.delete()
        return Response({'message': 'Product category deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 