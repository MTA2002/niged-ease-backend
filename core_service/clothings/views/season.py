from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from clothings.models.season import Season
from clothings.serializers.season import SeasonSerializer


class SeasonListView(APIView):
    @extend_schema(
        description="Get a list of all seasons",
        responses={200: SeasonSerializer(many=True)}
    )
    def get(self, request: Request):
        seasons = Season.objects.all()
        serializer = SeasonSerializer(seasons, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new season",
        request=SeasonSerializer,
        responses={
            201: SeasonSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request):
        serializer = SeasonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SeasonDetailView(APIView):
    def get_season(self, id):
        try:
            season = Season.objects.get(pk=id)
            return season
        except Season.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific season by ID",
        responses={
            200: SeasonSerializer,
            404: OpenApiResponse(description="Season not found")
        }
    )
    def get(self, request: Request, id):
        season = self.get_season(id)
        serializer = SeasonSerializer(season)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a season",
        request=SeasonSerializer,
        responses={
            200: SeasonSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Season not found")
        }
    )
    def put(self, request: Request, id):
        season = self.get_season(id)
        serializer = SeasonSerializer(season, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a season",
        responses={
            204: OpenApiResponse(description="Season deleted successfully"),
            404: OpenApiResponse(description="Season not found")
        }
    )
    def delete(self, request: Request, id):
        season = self.get_season(id)
        season.delete()
        return Response({'message': 'Season deleted successfully'}, status=status.HTTP_204_NO_CONTENT)