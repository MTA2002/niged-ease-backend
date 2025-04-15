from decimal import Decimal
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.inventory import Inventory
from inventory.models.store import Store
from inventory.models.product import Product
from inventory.serializers.product import ProductSerializer


class ProductListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all products",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request: Request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new product",
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            stores = Store.objects.filter(company_id=request.data.get('company_id')) # type: ignore
            for store in stores:
              Inventory.objects.create(
                product=product,
                store=store,
                quantity=Decimal('0')
            )
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get_product(self, id):
        try:
            product = Product.objects.get(pk=id)
            return product
        except Product.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific product by ID",
        responses={
            200: ProductSerializer,
            404: "Product not found"
        }
    )
    def get(self, request: Request, id):
        product = self.get_product(id)
        serializer = ProductSerializer(product)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a product",
        request_body=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: "Invalid data",
            404: "Product not found"
        }
    )
    def put(self, request: Request, id):
        product = self.get_product(id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a product",
        responses={
            204: "Product deleted successfully",
            404: "Product not found"
        }
    )
    def delete(self, request: Request, id):
        product = self.get_product(id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 