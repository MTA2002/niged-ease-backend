from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from inventory.models.product_category import ProductCategory
from inventory.serializers.product_category import ProductCategorySerializer


class ProductCategoryListView(APIView):
    @extend_schema(
        description="Get a list of all product categories",
        responses={200: ProductCategorySerializer(many=True)}
    )
    def get(self, request: Request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new product category",
        request=ProductCategorySerializer,
        responses={
            201: ProductCategorySerializer,
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific product category by ID",
        responses={
            200: ProductCategorySerializer,
            404: OpenApiResponse(description="Product category not found")
        }
    )
    def get(self, request: Request, id):
        category = self.get_category(id)
        serializer = ProductCategorySerializer(category)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a product category",
        request=ProductCategorySerializer,
        responses={
            200: ProductCategorySerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Product category not found")
        }
    )
    def put(self, request: Request, id):
        category = self.get_category(id)
        serializer = ProductCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a product category",
        responses={
            204: OpenApiResponse(description="Product category deleted successfully"),
            404: OpenApiResponse(description="Product category not found")
        }
    )
    def delete(self, request: Request, id):
        category = self.get_category(id)
        category.delete()
        return Response({'message': 'Product category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)