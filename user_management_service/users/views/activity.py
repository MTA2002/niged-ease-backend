from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.models.activity import ActivityLog
from users.serializers.activity import ActivityLogSerializer


class ActivityLogView(APIView):
    @extend_schema(
        summary="List activity logs",
        description="Get a list of all activity logs",
        tags=['Activity Logs'],
        responses={200: ActivityLogSerializer(many=True)}
    )
    def get(self, request: Request):
        activity_logs = ActivityLog.objects.all()
        serializer = ActivityLogSerializer(activity_logs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
  
    @extend_schema(
        summary="Create activity log",
        description="Create a new activity log",
        tags=['Activity Logs'],
        request=ActivityLogSerializer,
        responses={
            201: ActivityLogSerializer,
            400: OpenApiResponse(description="Bad Request")
        }
    )
    def post(self, request: Request):
        serializer = ActivityLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivityLogDetailView(APIView):
    def get_activity_log(self, id):
        try:
            activity_log = ActivityLog.objects.get(pk=id)
            return activity_log
        except ActivityLog.DoesNotExist:
            raise Http404
    
    @extend_schema(
        summary="Get activity log detail",
        description="Get details of a specific activity log",
        tags=['Activity Logs'],
        responses={
            200: ActivityLogSerializer,
            404: OpenApiResponse(description="Not Found")
        }
    )
    def get(self, request: Request, id):
        activity_log = self.get_activity_log(id)
        serializer = ActivityLogSerializer(activity_log)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
  
    @extend_schema(
        summary="Update activity log",
        description="Update an existing activity log",
        tags=['Activity Logs'],
        request=ActivityLogSerializer,
        responses={
            200: ActivityLogSerializer,
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Not Found")
        }
    )
    def put(self, request: Request, id):
        activity_log = self.get_activity_log(id)
        serializer = ActivityLogSerializer(activity_log, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete activity log",
        description="Delete an activity log",
        tags=['Activity Logs'],
        responses={
            204: OpenApiResponse(description="Activity log deleted successfully"),
            404: OpenApiResponse(description="Not Found")
        }
    )
    def delete(self, request: Request, id):
        activity_log = self.get_activity_log(id)
        activity_log.delete()
        return Response({'message': 'Activity log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)