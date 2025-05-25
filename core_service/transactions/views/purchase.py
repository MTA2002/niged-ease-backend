# type: ignore
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from inventory.models.inventory import Inventory
from transactions.models.purchase import Purchase
from transactions.models.purchase_item import PurchaseItem
from transactions.serializers.purchase import PurchaseSerializer
from transactions.serializers.purchase_item import PurchaseItemSerializer
from rest_framework import serializers
import os
import requests

class PurchaseListView(APIView):
    @extend_schema(
        description="Get a list of all purchases for a specific store",
        responses={200: PurchaseSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        purchases = Purchase.objects.filter(store_id=store_id)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new purchase with associated purchase items and update inventory for a specific store",
        request=PurchaseSerializer,
        responses={
            201: PurchaseSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        purchase_serializer = PurchaseSerializer(data=request.data)
        
        if purchase_serializer.is_valid():
            try:
                # Save purchase and let serializer create the items
                purchase_serializer.save()
                return Response(purchase_serializer.data, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseDetailView(APIView):
    def get_purchase(self, id, store_id):
        try:
            purchase = Purchase.objects.get(pk=id, store_id=store_id)
            return purchase
        except Purchase.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific purchase by ID for a specific store",
        responses={
            200: PurchaseSerializer,
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def get(self, request: Request, id, store_id):
        purchase = self.get_purchase(id, store_id)
        serializer = PurchaseSerializer(purchase)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a purchase, including its associated purchase items, and update inventory for a specific store",
        request=PurchaseSerializer,
        responses={
            200: PurchaseSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def put(self, request: Request, id, store_id):
        purchase = self.get_purchase(id, store_id)
        request.data['store_id'] = store_id
        
        # Store the items data but don't remove it from request
        items_data = request.data.get('items', [])
        
        # First, delete existing items
        PurchaseItem.objects.filter(purchase=purchase).delete()
        
        # Now update the purchase with all data including items
        purchase_serializer = PurchaseSerializer(purchase, data=request.data)
        
        if purchase_serializer.is_valid():
            try:
                purchase_serializer.save()
                
                # Get the newly created items
                
                
                return Response(purchase_serializer.data, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a purchase for a specific store",
        responses={
            204: OpenApiResponse(description="Purchase deleted successfully"),
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        purchase = self.get_purchase(id, store_id)
        purchase.delete()
        return Response({'message': 'Purchase deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class PurchaseItemListView(APIView):
    @extend_schema(
        description="Get a list of all purchase items for a specific purchase",
        responses={200: PurchaseItemSerializer(many=True)}
    )
    def get(self, request: Request, purchase_id, store_id=None):
        items = PurchaseItem.objects.filter(purchase_id=purchase_id)
        serializer = PurchaseItemSerializer(items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new purchase item for a specific purchase and update inventory",
        request=PurchaseItemSerializer,
        responses={
            201: PurchaseItemSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def post(self, request: Request, purchase_id, store_id=None):
        try:
            purchase = Purchase.objects.get(id=purchase_id, store_id=store_id)
            request.data['purchase'] = purchase_id # type: ignore
            serializer = PurchaseItemSerializer(data=request.data)
            if serializer.is_valid():
                purchase_item = serializer.save()
                try:
                    purchase.update_inventory([purchase_item])
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                except ValueError as e:
                    purchase_item.delete()
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)


class PurchaseItemDetailView(APIView):
    def get_item(self, purchase_id, item_id):
        try:
            item = PurchaseItem.objects.get(purchase_id=purchase_id, pk=item_id)
            return item
        except PurchaseItem.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific purchase item by ID",
        responses={
            200: PurchaseItemSerializer,
            404: OpenApiResponse(description="Purchase item not found")
        }
    )
    def get(self, request: Request, purchase_id, item_id, store_id=None):
        item = self.get_item(purchase_id, item_id)
        serializer = PurchaseItemSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a purchase item and adjust inventory accordingly",
        request=PurchaseItemSerializer,
        responses={
            200: PurchaseItemSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Purchase or item not found")
        }
    )
    def put(self, request: Request, purchase_id, item_id, store_id=None):
        try:
            purchase = Purchase.objects.get(id=purchase_id, store_id=store_id)
            item = self.get_item(purchase_id, item_id)
            
            request.data['purchase'] = purchase_id # type: ignore
            serializer = PurchaseItemSerializer(item, data=request.data)
            if serializer.is_valid():
                
                
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
                

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Delete a purchase item and adjust inventory accordingly",
        responses={
            204: OpenApiResponse(description="Purchase item deleted successfully"),
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Purchase or item not found")
        }
    )
    def delete(self, request: Request, purchase_id, item_id, store_id=None):
        try:
            purchase = Purchase.objects.get(id=purchase_id, store_id=store_id)
            item = self.get_item(purchase_id, item_id)
            
            try:
                inventory = Inventory.objects.get(
                    product=item.product,
                    store=purchase.store_id
                )
                inventory.quantity -= item.quantity
                inventory.save()
            except Inventory.DoesNotExist:
                return Response(
                    {'error': f'No inventory record found for product {item.product.name} in store {purchase.store_id.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.delete()
            requests.post(os.getenv('USER_SERVICE_URL') + '/activity-logs/', json={
            "user": request.user.id,
            'action': 'deleted sales',
            'description': 'deleted sales with id ' + str(purchase_id),
        },  headers={'Authorization': request.headers.get('Authorization')})
            
            return Response({'message': 'Purchase item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)