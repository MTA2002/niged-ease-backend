from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from inventory.models.store import Store
from inventory.serializers.store import StoreSerializer


class StoreListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all stores",
        responses={200: StoreSerializer(many=True)}
    )
    def get(self, request: Request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new store",
        request_body=StoreSerializer,
        responses={
            201: StoreSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StoreDetailView(APIView):
    def get_store(self, id):
        try:
            store = Store.objects.get(pk=id)
            return store
        except Store.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific store by ID",
        responses={
            200: StoreSerializer,
            404: "Store not found"
        }
    )
    def get(self, request: Request, id):
        store = self.get_store(id)
        serializer = StoreSerializer(store)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a store",
        request_body=StoreSerializer,
        responses={
            200: StoreSerializer,
            400: "Invalid data",
            404: "Store not found"
        }
    )
    def put(self, request: Request, id):
        store = self.get_store(id)
        serializer = StoreSerializer(store, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a store",
        responses={
            204: "Store deleted successfully",
            404: "Store not found"
        }
    )
    def delete(self, request: Request, id):
        store = self.get_store(id)
        store.delete()
        return Response({'message': 'Store deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 