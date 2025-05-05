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


class PurchaseListView(APIView):
    @extend_schema(
        description="Get a list of all purchases",
        responses={200: PurchaseSerializer(many=True)}
    )
    def get(self, request: Request):
        purchases = Purchase.objects.all()
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new purchase with associated purchase items and update inventory",
        request=PurchaseSerializer,
        responses={
            201: PurchaseSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )

    
    def post(self, request: Request):
        purchase_items_data = request.data.pop('items', []) # type: ignore
        purchase_serializer = PurchaseSerializer(data=request.data)
        
        if purchase_serializer.is_valid():
            purchase = purchase_serializer.save()
            
            purchase_items = []
            for item_data in purchase_items_data:
                item_data['purchase'] = purchase.id # type: ignore
                item_serializer = PurchaseItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    purchase_item = item_serializer.save()
                    purchase_items.append(purchase_item)
                else:
                    purchase.delete()
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                purchase.update_inventory(purchase_items)
            except ValueError as e:
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
    
    @extend_schema(
        description="Get a specific purchase by ID",
        responses={
            200: PurchaseSerializer,
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def get(self, request: Request, id):
        purchase = self.get_purchase(id)
        serializer = PurchaseSerializer(purchase)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a purchase, including its associated purchase items, and update inventory",
        request=PurchaseSerializer,
        responses={
            200: PurchaseSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def put(self, request: Request, id):
        purchase = self.get_purchase(id)
        purchase_items_data = request.data.pop('items', []) # type: ignore
        purchase_serializer = PurchaseSerializer(purchase, data=request.data)
        
        if purchase_serializer.is_valid():
            purchase = purchase_serializer.save()
            PurchaseItem.objects.filter(purchase=purchase).delete()
            
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
                purchase.update_inventory(purchase_items)
            except ValueError as e:
                purchase.delete()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(purchase_serializer.data, status=status.HTTP_200_OK)
        return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a purchase",
        responses={
            204: OpenApiResponse(description="Purchase deleted successfully"),
            404: OpenApiResponse(description="Purchase not found")
        }
    )
    def delete(self, request: Request, id):
        purchase = self.get_purchase(id)
        purchase.delete()
        return Response({'message': 'Purchase deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class PurchaseItemListView(APIView):
    @extend_schema(
        description="Get a list of all purchase items for a specific purchase",
        responses={200: PurchaseItemSerializer(many=True)}
    )
    def get(self, request: Request, purchase_id):
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
    def post(self, request: Request, purchase_id):
        try:
            purchase = Purchase.objects.get(id=purchase_id)
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
    def get(self, request: Request, purchase_id, item_id):
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
    def put(self, request: Request, purchase_id, item_id):
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            item = self.get_item(purchase_id, item_id)
            old_quantity = item.quantity
            
            request.data['purchase'] = purchase_id # type: ignore
            serializer = PurchaseItemSerializer(item, data=request.data)
            if serializer.is_valid():
                try:
                    inventory = Inventory.objects.get(
                        product=item.product,
                        store=purchase.store
                    )
                    inventory.quantity -= old_quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    return Response(
                        {'error': f'No inventory record found for product {item.product.name} in store {purchase.store.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                updated_item = serializer.save()
                
                try:
                    purchase.update_inventory([updated_item])
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                except ValueError as e:
                    inventory.quantity += updated_item.quantity
                    inventory.save()
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
    def delete(self, request: Request, purchase_id, item_id):
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            item = self.get_item(purchase_id, item_id)
            
            try:
                inventory = Inventory.objects.get(
                    product=item.product,
                    store=purchase.store
                )
                inventory.quantity -= item.quantity
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