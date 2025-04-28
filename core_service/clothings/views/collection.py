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
    def get(self, request: Request):
        collections = Collection.objects.all()
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
    def post(self, request: Request):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionDetailView(APIView):
    def get_collection(self, id):
        try:
            collection = Collection.objects.get(pk=id)
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
    def get(self, request: Request, id):
        collection = self.get_collection(id)
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
    def put(self, request: Request, id):
        collection = self.get_collection(id)
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
    def delete(self, request: Request, id):
        collection = self.get_collection(id)
        collection.delete()
        return Response({'message': 'Collection deleted successfully'}, status=status.HTTP_204_NO_CONTENT)