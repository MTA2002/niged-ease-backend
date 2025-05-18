#type:ignore
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from inventory.models.inventory import Inventory
from inventory.serializers.inventory import InventorySerializer
from companies.models.store import Store


class InventoryListView(APIView):
    @extend_schema(
        description="Get a list of all inventory items for a specific store",
        responses={200: InventorySerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        inventories = Inventory.objects.filter(store_id=store_id)
        serializer = InventorySerializer(inventories, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new inventory item for a specific store",
        request=InventorySerializer,
        responses={
            201: InventorySerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        store = Store.objects.get(id=store_id)
        request.data['store'] = store_id
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryDetailView(APIView):
    def get_inventory(self, id, store_id):
        try:
            inventory = Inventory.objects.get(pk=id, store_id=store_id)
            return inventory
        except Inventory.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific inventory item by ID for a specific store",
        responses={
            200: InventorySerializer,
            404: OpenApiResponse(description="Inventory item not found")
        }
    )
    def get(self, request: Request, id, store_id):
        inventory = self.get_inventory(id, store_id)
        serializer = InventorySerializer(inventory)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update an inventory item for a specific store",
        request=InventorySerializer,
        responses={
            200: InventorySerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Inventory item not found")
        }
    )
    def put(self, request: Request, id, store_id):
        inventory = self.get_inventory(id, store_id)
        store = Store.objects.get(id=store_id)
        request.data['store'] = store_id
        serializer = InventorySerializer(inventory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete an inventory item for a specific store",
        responses={
            204: OpenApiResponse(description="Inventory item deleted successfully"),
            404: OpenApiResponse(description="Inventory item not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        inventory = self.get_inventory(id, store_id)
        inventory.delete()
        return Response({'message': 'Inventory item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)