from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from financials.models.receivable import Receivable
from financials.serializers.receivable import ReceivableSerializer


class ReceivableListView(APIView):
    @extend_schema(
        description="Get a list of all receivables",
        responses={200: ReceivableSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        receivables = Receivable.objects.filter(store_id=store_id)
        serializer = ReceivableSerializer(receivables, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new receivable",
        request=ReceivableSerializer,
        responses={
            201: ReceivableSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        serializer = ReceivableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceivableDetailView(APIView):
    def get_receivable(self, id, store_id):
        try:
            receivable = Receivable.objects.get(pk=id, store_id=store_id)
            return receivable
        except Receivable.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific receivable by ID",
        responses={
            200: ReceivableSerializer,
            404: OpenApiResponse(description="Receivable not found")
        }
    )
    def get(self, request: Request, id, store_id):
        receivable = self.get_receivable(id, store_id)
        serializer = ReceivableSerializer(receivable)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a receivable",
        request=ReceivableSerializer,
        responses={
            200: ReceivableSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Receivable not found")
        }
    )
    def put(self, request: Request, id, store_id):
        receivable = self.get_receivable(id, store_id)
        serializer = ReceivableSerializer(receivable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a receivable",
        responses={
            204: OpenApiResponse(description="Receivable deleted successfully"),
            404: OpenApiResponse(description="Receivable not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        receivable = self.get_receivable(id, store_id)
        receivable.delete()
        return Response({'message': 'Receivable deleted successfully'}, status=status.HTTP_204_NO_CONTENT)