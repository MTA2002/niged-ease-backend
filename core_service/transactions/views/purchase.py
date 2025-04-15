from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.inventory import Inventory
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
                item_data['purchase'] = purchase.id  # type: ignore
                item_serializer = PurchaseItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    purchase_item = item_serializer.save()
                    purchase_items.append(purchase_item)
                else:
                    purchase.delete()  # type: ignore # Rollback if item creation fails
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                purchase.update_inventory(purchase_items) # type: ignore
            except ValueError as e:
                # Rollback the purchase if inventory update fails
                purchase.delete() # type: ignore
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
        purchase_items_data = request.data.pop('items', []) # type: ignore
        purchase_serializer = PurchaseSerializer(purchase, data=request.data)
        
        if purchase_serializer.is_valid():
            purchase = purchase_serializer.save()
            
            # Delete existing items
            PurchaseItem.objects.filter(purchase=purchase).delete()
            
            # Create new items
            purchase_items = []
            for item_data in purchase_items_data:
                item_data['purchase'] = purchase.id # type: ignore
                item_serializer = PurchaseItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    purchase_item = item_serializer.save()
                    purchase_items.append(purchase_item)
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                purchase.update_inventory(purchase_items) # type: ignore
            except ValueError as e:
                # Rollback the purchase if inventory update fails
                purchase.delete() # type: ignore
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
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            request.data['purchase'] = purchase_id # type: ignore
            serializer = PurchaseItemSerializer(data=request.data)
            if serializer.is_valid():
                purchase_item = serializer.save()
                try:
                    # Update inventory for the new item
                    purchase.update_inventory([purchase_item])
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                except ValueError as e:
                    # Rollback the purchase item if inventory update fails
                    purchase_item.delete() # type: ignore
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
    
    def get(self, request: Request, purchase_id, item_id):
        item = self.get_item(purchase_id, item_id)
        serializer = PurchaseItemSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, purchase_id, item_id):
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            item = self.get_item(purchase_id, item_id)
            old_quantity = item.quantity  # Store old quantity for inventory adjustment
            
            request.data['purchase'] = purchase_id # type: ignore
            serializer = PurchaseItemSerializer(item, data=request.data)
            if serializer.is_valid():
                # First, restore the old quantity to inventory
                try:
                    inventory = Inventory.objects.get(
                        product=item.product,
                        store=purchase.store
                    )
                    inventory.quantity -= old_quantity  # Subtract old quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    return Response(
                        {'error': f'No inventory record found for product {item.product.name} in store {purchase.store.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update the purchase item
                updated_item = serializer.save()
                
                try:
                    # Update inventory with the new quantity
                    purchase.update_inventory([updated_item])
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                except ValueError as e:
                    # Rollback the inventory update
                    inventory.quantity += updated_item.quantity # type: ignore
                    inventory.save()
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request, purchase_id, item_id):
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            item = self.get_item(purchase_id, item_id)
            
            # Restore the quantity to inventory before deleting
            try:
                inventory = Inventory.objects.get(
                    product=item.product,
                    store=purchase.store
                )
                inventory.quantity -= item.quantity  # Subtract the quantity
                inventory.save()
            except Inventory.DoesNotExist:
                return Response(
                    {'error': f'No inventory record found for product {item.product.name} in store {purchase.store.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.delete()
            return Response({'message': 'Purchase item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND) 