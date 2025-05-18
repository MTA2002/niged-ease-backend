from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from clothings.models.collection import Collection
from clothings.serializers.collection import CollectionSerializer


class CollectionListView(APIView):
    @extend_schema(
        description="Get a list of all collections",
        responses={200: CollectionSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        collections = Collection.objects.filter(store_id=store_id)
        serializer = CollectionSerializer(collections, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new collection",
        request=CollectionSerializer,
        responses={
            201: CollectionSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        # Add store_id to request data if it's not there
        request_data = request.data.copy() # type: ignore
        
        # Make sure store_id is used from the URL path parameter
        # request_data['store_id'] = store_id
        
        # Debug the incoming data
        print("POST request data:", request_data)
        
        serializer = CollectionSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
        # If validation fails, print the errors
        print("Validation errors:", serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionDetailView(APIView):
    def get_collection(self, id, store_id):
        try:
            collection = Collection.objects.get(pk=id, store_id=store_id)
            return collection
        except Collection.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific collection by ID",
        responses={
            200: CollectionSerializer,
            404: OpenApiResponse(description="Collection not found")
        }
    )
    def get(self, request: Request, id, store_id):
        collection = self.get_collection(id, store_id)
        serializer = CollectionSerializer(collection)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a collection",
        request=CollectionSerializer,
        responses={
            200: CollectionSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Collection not found")
        }
    )
    def put(self, request: Request, id, store_id):
        collection = self.get_collection(id, store_id)
        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a collection",
        responses={
            204: OpenApiResponse(description="Collection deleted successfully"),
            404: OpenApiResponse(description="Collection not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        collection = self.get_collection(id, store_id)
        collection.delete()
        return Response({'message': 'Collection deleted successfully'}, status=status.HTTP_204_NO_CONTENT)