from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.db.models import Q
from decimal import Decimal
from inventory.models.stock_transfer import StockTransfer
from inventory.serializers.stock_transfer import StockTransferSerializer
from inventory.models.inventory import Inventory

class StockTransferListView(APIView):

    @extend_schema(
        description="Get a list of all stock transfers for a specific store (both incoming and outgoing)",
        parameters=[
            OpenApiParameter(
                name="store_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the store to get transfers for"
            )
        ],
        responses={
            200: StockTransferSerializer(many=True),
            404: OpenApiResponse(description="Store not found")
        }
    )
    def get(self, request: Request, store_id):
        transfers = StockTransfer.objects.filter(
            Q(source_store=store_id) | Q(destination_store=store_id)
        ).select_related('source_store', 'destination_store', 'product')
        serializer = StockTransferSerializer(transfers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new stock transfer from this store to another store",
        parameters=[
            OpenApiParameter(
                name="store_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the source store"
            )
        ],
        request=StockTransferSerializer,
        responses={
            201: StockTransferSerializer,
            400: OpenApiResponse(
                description="Invalid data - Insufficient stock, same store transfer, or invalid input"
            ),
            404: OpenApiResponse(description="Store or product not found")
        }
    )
    def post(self, request: Request, store_id):
        # Set source store from URL
        
        serializer = StockTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockTransferDetailView(APIView):

    def get_transfer(self, id, store_id):
        try:
            transfer = StockTransfer.objects.get(
                Q(source_store=store_id) | Q(destination_store=store_id),
                pk=id
            )
            return transfer
        except StockTransfer.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get details of a specific stock transfer",
        parameters=[
            OpenApiParameter(
                name="store_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the store"
            ),
            OpenApiParameter(
                name="id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the transfer"
            )
        ],
        responses={
            200: StockTransferSerializer,
            404: OpenApiResponse(description="Transfer not found")
        }
    )
    def get(self, request: Request, id, store_id):
        transfer = self.get_transfer(id, store_id)
        serializer = StockTransferSerializer(transfer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a pending stock transfer (only by source store)",
        parameters=[
            OpenApiParameter(
                name="store_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the source store"
            ),
            OpenApiParameter(
                name="id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the transfer to update"
            )
        ],
        request=StockTransferSerializer,
        responses={
            200: StockTransferSerializer,
            400: OpenApiResponse(description="Invalid data or transfer not in pending state"),
            404: OpenApiResponse(description="Transfer not found")
        }
    )
    def put(self, request: Request, id, store_id):
        transfer = self.get_transfer(id, store_id)
        
        # Only source store can update
        if transfer.source_store.id != store_id:
            return Response(
                {"detail": "Only source store can update the transfer"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StockTransferSerializer(transfer, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Cancel a pending transfer (only by source store)",
        parameters=[
            OpenApiParameter(
                name="store_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the store"
            ),
            OpenApiParameter(
                name="id",
                type=str,
                location=OpenApiParameter.PATH,
                description="UUID of the transfer to cancel"
            )
        ],
        responses={
            200: OpenApiResponse(description="Transfer cancelled successfully"),
            400: OpenApiResponse(description="Transfer not in pending state"),
            403: OpenApiResponse(description="Not authorized to cancel transfer"),
            404: OpenApiResponse(description="Transfer not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        transfer = self.get_transfer(id, store_id)
        
        # Only source store can cancel
        if transfer.source_store.id != store_id:
            return Response(
                {"detail": "Only source store can cancel the transfer"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        # Return the quantity to source inventory
        source_inventory = Inventory.objects.select_for_update().get(
            store=transfer.source_store,
            product=transfer.product
        )
        source_inventory.quantity += Decimal(str(transfer.quantity))
        source_inventory.save()

        destination_inventory = Inventory.objects.select_for_update().get(
            store=transfer.destination_store,
            product=transfer.product
        )
        
        destination_inventory.quantity -= Decimal(str(transfer.quantity))
        source_inventory.save()
            
        # Mark as cancelled
        transfer.status = StockTransfer.CANCELLED
        transfer.save()
        
        return Response(
            {'message': 'Transfer cancelled successfully'},
            status=status.HTTP_200_OK
        ) 