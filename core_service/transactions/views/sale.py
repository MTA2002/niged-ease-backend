# type: ignore
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from transactions.models.sale import Sale
from transactions.models.sale_item import SaleItem
from transactions.serializers.sale import SaleSerializer
from transactions.serializers.sale_item import SaleItemSerializer
from inventory.models.inventory import Inventory


class SaleListView(APIView):
    @extend_schema(
        description="Get a list of all sales",
        responses={200: SaleSerializer(many=True)}
    )
    def get(self, request: Request):
        sales = Sale.objects.all()
        serializer = SaleSerializer(sales, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new sale with associated sale items and update inventory",
        request=SaleSerializer,
        responses={
            201: SaleSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        sale_items_data = request.data.pop('items', []) 
        sale_serializer = SaleSerializer(data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            
            sale_items = []
            for item_data in sale_items_data:
                item_data['sale'] = sale.id
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    sale_item = item_serializer.save()
                    sale_items.append(sale_item)
                else:
                    sale.delete()
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                sale.update_inventory(sale_items)
            except ValueError as e:
                sale.delete()
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
    
    @extend_schema(
        description="Get a specific sale by ID",
        responses={
            200: SaleSerializer,
            404: OpenApiResponse(description="Sale not found")
        }
    )
    def get(self, request: Request, id):
        sale = self.get_sale(id)
        serializer = SaleSerializer(sale)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a sale, including its associated sale items, and update inventory",
        request=SaleSerializer,
        responses={
            200: SaleSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Sale not found")
        }
    )
    def put(self, request: Request, id):
        sale = self.get_sale(id)
        sale_items_data = request.data.pop('items', [])
        sale_serializer = SaleSerializer(sale, data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            SaleItem.objects.filter(sale=sale).delete()
            
            sale_items = []
            for item_data in sale_items_data:
                item_data['sale'] = sale.id
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    sale_item = item_serializer.save()
                    sale_items.append(sale_item)
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                sale.update_inventory(sale_items)
            except ValueError as e:
                sale.delete()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(sale_serializer.data, status=status.HTTP_200_OK)
        return Response(sale_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a sale",
        responses={
            204: OpenApiResponse(description="Sale deleted successfully"),
            404: OpenApiResponse(description="Sale not found")
        }
    )
    def delete(self, request: Request, id):
        sale = self.get_sale(id)
        sale.delete()
        return Response({'message': 'Sale deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class SaleItemListView(APIView):
    @extend_schema(
        description="Get a list of all sale items for a specific sale",
        responses={200: SaleItemSerializer(many=True)}
    )
    def get(self, request: Request, sale_id):
        items = SaleItem.objects.filter(sale_id=sale_id)
        serializer = SaleItemSerializer(items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new sale item for a specific sale and update inventory",
        request=SaleItemSerializer,
        responses={
            201: SaleItemSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Sale not found")
        }
    )
    def post(self, request: Request, sale_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            request.data['sale'] = sale_id
            serializer = SaleItemSerializer(data=request.data)
            if serializer.is_valid():
                sale_item = serializer.save()
                try:
                    sale.update_inventory([sale_item])
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                except ValueError as e:
                    sale_item.delete()
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
    
    @extend_schema(
        description="Get a specific sale item by ID",
        responses={
            200: SaleItemSerializer,
            404: OpenApiResponse(description="Sale item not found")
        }
    )
    def get(self, request: Request, sale_id, item_id):
        item = self.get_item(sale_id, item_id)
        serializer = SaleItemSerializer(item)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a sale item and adjust inventory accordingly",
        request=SaleItemSerializer,
        responses={
            200: SaleItemSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Sale or item not found")
        }
    )
    def put(self, request: Request, sale_id, item_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            item = self.get_item(sale_id, item_id)
            old_quantity = item.quantity
            
            request.data['sale'] = sale_id
            serializer = SaleItemSerializer(item, data=request.data)
            if serializer.is_valid():
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
                
                updated_item = serializer.save()
                
                try:
                    sale.update_inventory([updated_item])
                    return Response(data=serializer.data, status=status.HTTP_200_OK)
                except ValueError as e:
                    inventory.quantity -= updated_item.quantity
                    inventory.save()
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Sale.DoesNotExist:
            return Response({'error': 'Sale not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        description="Delete a sale item and adjust inventory accordingly",
        responses={
            204: OpenApiResponse(description="Sale item deleted successfully"),
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Sale or item not found")
        }
    )
    def delete(self, request: Request, sale_id, item_id):
        try:
            sale = Sale.objects.get(id=sale_id)
            item = self.get_item(sale_id, item_id)
            
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