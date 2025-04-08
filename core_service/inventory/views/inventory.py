from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.inventory import Inventory
from inventory.serializers.inventory import InventorySerializer


class InventoryListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all inventory items",
        responses={200: InventorySerializer(many=True)}
    )
    def get(self, request: Request):
        inventories = Inventory.objects.all()
        serializer = InventorySerializer(inventories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new inventory item",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id', 'store_id', 'quantity'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Product ID'),
                'store_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Store ID'),
                'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity'),
            },
        ),
        responses={
            201: InventorySerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryDetailView(APIView):
    def get_inventory(self, id):
        try:
            inventory = Inventory.objects.get(pk=id)
            return inventory
        except Inventory.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific inventory item by ID",
        responses={
            200: InventorySerializer,
            404: "Inventory item not found"
        }
    )
    def get(self, request: Request, id):
        inventory = self.get_inventory(id)
        serializer = InventorySerializer(inventory)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an inventory item",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Product ID'),
                'store_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid', description='Store ID'),
                'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantity'),
            },
        ),
        responses={
            200: InventorySerializer,
            400: "Invalid data",
            404: "Inventory item not found"
        }
    )
    def put(self, request: Request, id):
        inventory = self.get_inventory(id)
        serializer = InventorySerializer(inventory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an inventory item",
        responses={
            204: "Inventory item deleted",
            404: "Inventory item not found"
        }
    )
    def delete(self, request: Request, id):
        inventory = self.get_inventory(id)
        inventory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 