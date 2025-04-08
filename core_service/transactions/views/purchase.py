from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models.purchase import Purchase
from transactions.models.purchase_item import PurchaseItem
from transactions.serializers.purchase import PurchaseSerializer
from transactions.serializers.purchase_item import PurchaseItemSerializer


class PurchaseListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all purchases",
        responses={200: PurchaseSerializer(many=True)}
    )
    def get(self, request: Request):
        purchases = Purchase.objects.all()
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new purchase",
        request_body=PurchaseSerializer,
        responses={
            201: PurchaseSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        # Handle nested purchase items
        purchase_items_data = request.data.pop('items', []) # type: ignore
        purchase_serializer = PurchaseSerializer(data=request.data)
        
        if purchase_serializer.is_valid():
            purchase = purchase_serializer.save() 
            
            # Create purchase items
            purchase_items = []
            for item_data in purchase_items_data:
                item_data['purchase'] = purchase.id 
                item_serializer = PurchaseItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    purchase_item = item_serializer.save()
                    purchase_items.append(purchase_item)
                else:
                    purchase.delete()  # Rollback if item creation fails
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                purchase.update_inventory(purchase_items)
            except ValueError as e:
                # Rollback the purchase if inventory update fails
                purchase.delete()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(purchase_serializer.data, status=status.HTTP_201_CREATED)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseDetailView(APIView):
    def get_purchase(self, id):
        try:
            purchase = Purchase.objects.get(pk=id)
            return purchase
        except Purchase.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific purchase by ID",
        responses={
            200: PurchaseSerializer,
            404: "Purchase not found"
        }
    )
    def get(self, request: Request, id):
        purchase = self.get_purchase(id)
        serializer = PurchaseSerializer(purchase)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a purchase",
        request_body=PurchaseSerializer,
        responses={
            200: PurchaseSerializer,
            400: "Invalid data",
            404: "Purchase not found"
        }
    )
    def put(self, request: Request, id):
        purchase = self.get_purchase(id)
        
        # Handle nested purchase items
        purchase_items_data = request.data.pop('items', [])
        purchase_serializer = PurchaseSerializer(purchase, data=request.data)
        
        if purchase_serializer.is_valid():
            purchase = purchase_serializer.save()
            
            # Delete existing items
            PurchaseItem.objects.filter(purchase=purchase).delete()
            
            # Create new items
            purchase_items = []
            for item_data in purchase_items_data:
                item_data['purchase'] = purchase.id
                item_serializer = PurchaseItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    purchase_item = item_serializer.save()
                    purchase_items.append(purchase_item)
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                purchase.update_inventory(purchase_items)
            except ValueError as e:
                # Rollback the purchase if inventory update fails
                purchase.delete()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(purchase_serializer.data, status=status.HTTP_200_OK)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a purchase",
        responses={
            204: "Purchase deleted successfully",
            404: "Purchase not found"
        }
    )
    def delete(self, request: Request, id):
        purchase = self.get_purchase(id)
        purchase.delete()
        return Response({'message': 'Purchase deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class PurchaseItemListView(APIView):
    def get(self, request: Request, purchase_id):
        items = PurchaseItem.objects.filter(purchase_id=purchase_id)
        serializer = PurchaseItemSerializer(items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Request, purchase_id):
        request.data['purchase'] = purchase_id
        serializer = PurchaseItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseItemDetailView(APIView):
    def get_item(self, purchase_id, item_id):
        try:
            item = PurchaseItem.objects.get(purchase_id=purchase_id, pk=item_id)
            return item
        except PurchaseItem.DoesNotExist:
            raise Http404
    
    def get(self, request: Request, purchase_id, item_id):
        item = self.get_item(purchase_id, item_id)
        serializer = PurchaseItemSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, purchase_id, item_id):
        item = self.get_item(purchase_id, item_id)
        request.data['purchase'] = purchase_id
        serializer = PurchaseItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, purchase_id, item_id):
        item = self.get_item(purchase_id, item_id)
        item.delete()
        return Response({'message': 'Purchase item deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 