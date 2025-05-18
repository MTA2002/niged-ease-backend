from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from clothings.models.color import Color
from clothings.serializers.color import ColorSerializer


class ColorListView(APIView):
    @extend_schema(
        description="Get a list of all colors",
        responses={200: ColorSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        colors = Color.objects.filter(store_id=store_id)
        serializer = ColorSerializer(colors, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new color",
        request=ColorSerializer,
        responses={
            201: ColorSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorDetailView(APIView):
    def get_color(self, id, store_id):
        try:
            color = Color.objects.get(pk=id, store_id=store_id)
            return color
        except Color.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific color by ID",
        responses={
            200: ColorSerializer,
            404: OpenApiResponse(description="Color not found")
        }
    )
    def get(self, request: Request, id, store_id):
        color = self.get_color(id, store_id)
        serializer = ColorSerializer(color)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a color",
        request=ColorSerializer,
        responses={
            200: ColorSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Color not found")
        }
    )
    def put(self, request: Request, id, store_id):
        color = self.get_color(id, store_id)
        serializer = ColorSerializer(color, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a color",
        responses={
            204: OpenApiResponse(description="Color deleted successfully"),
            404: OpenApiResponse(description="Color not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        color = self.get_color(id, store_id)
        color.delete()
        return Response({'message': 'Color deleted successfully'}, status=status.HTTP_204_NO_CONTENT)