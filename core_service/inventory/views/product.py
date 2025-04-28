from decimal import Decimal
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from inventory.models.inventory import Inventory
from inventory.models.store import Store
from inventory.models.product import Product
from inventory.serializers.product import ProductSerializer


class ProductListView(APIView):
    @extend_schema(
        description="Get a list of all products",
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request: Request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new product and initialize inventory for stores in the specified company",
        request=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific product by ID",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Product not found")
        }
    )
    def get(self, request: Request, id):
        product = self.get_product(id)
        serializer = ProductSerializer(product)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a product",
        request=ProductSerializer,
        responses={
            200: ProductSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Product not found")
        }
    )
    def put(self, request: Request, id):
        product = self.get_product(id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a product",
        responses={
            204: OpenApiResponse(description="Product deleted successfully"),
            404: OpenApiResponse(description="Product not found")
        }
    )
    def delete(self, request: Request, id):
        product = self.get_product(id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)