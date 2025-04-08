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
        sale_items_data = request.data.pop('items', [])
        sale_serializer = SaleSerializer(data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            
            # Create sale items
            for item_data in sale_items_data:
                item_data['sale'] = sale.id
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    item_serializer.save()
                else:
                    sale.delete()  # Rollback if item creation fails
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
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
        sale_items_data = request.data.pop('items', [])
        sale_serializer = SaleSerializer(sale, data=request.data)
        
        if sale_serializer.is_valid():
            sale = sale_serializer.save()
            
            # Delete existing items
            SaleItem.objects.filter(sale=sale).delete()
            
            # Create new items
            for item_data in sale_items_data:
                item_data['sale'] = sale.id
                item_serializer = SaleItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    item_serializer.save()
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
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
        request.data['sale'] = sale_id
        serializer = SaleItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        item = self.get_item(sale_id, item_id)
        request.data['sale'] = sale_id
        serializer = SaleItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, sale_id, item_id):
        item = self.get_item(sale_id, item_id)
        item.delete()
        return Response({'message': 'Sale item deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 