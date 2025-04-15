from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models.sale import Sale
from transactions.models.sale_item import SaleItem
from transactions.serializers.sale import SaleSerializer
from transactions.serializers.sale_item import SaleItemSerializer
from inventory.models.inventory import Inventory


class SaleListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all sales",
        responses={200: SaleSerializer(many=True)}
    )
    def get(self, request: Request):
        sales = Sale.objects.all()
        serializer = SaleSerializer(sales, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new sale",
        request_body=SaleSerializer,
        responses={
            201: SaleSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        # Handle nested sale items
        sale_items_data = request.data.pop('items', []) # type: ignore
        sale_serializer = SaleSerializer(data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            
            # Create sale items
            sale_items = []
            for item_data in sale_items_data:
                item_data['sale'] = sale.id # type: ignore
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    sale_item = item_serializer.save()
                    sale_items.append(sale_item)
                else:
                    sale.delete()  # type: ignore # Rollback if item creation fails
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                sale.update_inventory(sale_items) # type: ignore
            except ValueError as e:
                # Rollback the sale if inventory update fails
                sale.delete() # type: ignore
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(sale_serializer.data, status=status.HTTP_201_CREATED)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SaleDetailView(APIView):
    def get_sale(self, id):
        try:
            sale = Sale.objects.get(pk=id)
            return sale
        except Sale.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific sale by ID",
        responses={
            200: SaleSerializer,
            404: "Sale not found"
        }
    )
    def get(self, request: Request, id):
        sale = self.get_sale(id)
        serializer = SaleSerializer(sale)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a sale",
        request_body=SaleSerializer,
        responses={
            200: SaleSerializer,
            400: "Invalid data",
            404: "Sale not found"
        }
    )
    def put(self, request: Request, id):
        sale = self.get_sale(id)
        
        # Handle nested sale items
        sale_items_data = request.data.pop('items', []) # type: ignore
        sale_serializer = SaleSerializer(sale, data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            
            # Delete existing items
            SaleItem.objects.filter(sale=sale).delete()
            
            # Create new items
            sale_items = []
            for item_data in sale_items_data:
                item_data['sale'] = sale.id # type: ignore
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    sale_item = item_serializer.save()
                    sale_items.append(sale_item)
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Update inventory after all items are created
                sale.update_inventory(sale_items) # type: ignore
            except ValueError as e:
                # Rollback the sale if inventory update fails
                sale.delete() # type: ignore
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(sale_serializer.data, status=status.HTTP_200_OK)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a sale",
        responses={
            204: "Sale deleted successfully",
            404: "Sale not found"
        }
    )
    def delete(self, request: Request, id):
        sale = self.get_sale(id)
        sale.delete()
        return Response({'message': 'Sale deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class SaleItemListView(APIView):
    def get(self, request: Request, sale_id):
        items = SaleItem.objects.filter(sale_id=sale_id)
        serializer = SaleItemSerializer(items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Request, sale_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            request.data['sale'] = sale_id # type: ignore
            serializer = SaleItemSerializer(data=request.data)
            if serializer.is_valid():
                sale_item = serializer.save()
                try:
                    # Update inventory for the new item
                    sale.update_inventory([sale_item])
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                except ValueError as e:
                    # Rollback the sale item if inventory update fails
                    sale_item.delete() # type: ignore
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Sale.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND)


class SaleItemDetailView(APIView):
    def get_item(self, sale_id, item_id):
        try:
            item = SaleItem.objects.get(sale_id=sale_id, pk=item_id)
            return item
        except SaleItem.DoesNotExist:
            raise Http404
    
    def get(self, request: Request, sale_id, item_id):
        item = self.get_item(sale_id, item_id)
        serializer = SaleItemSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, sale_id, item_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            item = self.get_item(sale_id, item_id)
            old_quantity = item.quantity  # Store old quantity for inventory adjustment
            
            request.data['sale'] = sale_id # type: ignore
            serializer = SaleItemSerializer(item, data=request.data)
            if serializer.is_valid():
                # First, restore the old quantity to inventory
                try:
                    inventory = Inventory.objects.get(
                        product=item.product,
                        store=sale.store
                    )
                    inventory.quantity += old_quantity
                    inventory.save()
                except Inventory.DoesNotExist:
                    return Response(
                        {'error': f'No inventory record found for product {item.product.name} in store {sale.store.name}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update the sale item
                updated_item = serializer.save()
                
                try:
                    # Update inventory with the new quantity
                    sale.update_inventory([updated_item])
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                except ValueError as e:
                    # Rollback the inventory update
                    inventory.quantity -= updated_item.quantity # type: ignore
                    inventory.save()
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Sale.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request, sale_id, item_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            item = self.get_item(sale_id, item_id)
            
            # Restore the quantity to inventory before deleting
            try:
                inventory = Inventory.objects.get(
                    product=item.product,
                    store=sale.store
                )
                inventory.quantity += item.quantity
                inventory.save()
            except Inventory.DoesNotExist:
                return Response(
                    {'error': f'No inventory record found for product {item.product.name} in store {sale.store.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.delete()
            return Response({'message': 'Sale item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Sale.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND) 