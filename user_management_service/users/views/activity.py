from users.models.activity import ActivityLog
from users.serializers.activity import ActivityLogSerializer
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ActivityLogView(APIView):

  @swagger_auto_schema(
      operation_summary="List activity logs",
      operation_description="Get a list of all activity logs",
      tags=['Activity Logs'],
      responses={
          200: ActivityLogSerializer(many=True)
      }
  )
  def get(self, request: Request):
    activity_logs = ActivityLog.objects.all()
    serializer = ActivityLogSerializer(activity_logs, many = True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema(
      operation_summary="Create activity log",
      operation_description="Create a new activity log",
      tags=['Activity Logs'],
      request_body=ActivityLogSerializer,
      responses={
          201: ActivityLogSerializer,
          400: 'Bad Request'
      }
  )
  def post(self, request: Request):
    serializer = ActivityLogSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(data=serializer.data, status=status.HTTP_201_CREATED)

class ActivityLogDetailView(APIView):

  def get_activity_log(self, id):
    try:
      activity_log = ActivityLog.objects.get(pk = id)
      return activity_log
    except ActivityLog.DoesNotExist:
      raise Http404
    
  @swagger_auto_schema(
      operation_summary="Get activity log detail",
      operation_description="Get details of a specific activity log",
      tags=['Activity Logs'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="Activity Log ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      responses={
          200: ActivityLogSerializer,
          404: 'Not Found'
      }
  )
  def get(self, request: Request, id):
    activity_log = self.get_activity_log(id)
    serializer = ActivityLogSerializer(activity_log)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
  
  @swagger_auto_schema(
      operation_summary="Update activity log",
      operation_description="Update an existing activity log",
      tags=['Activity Logs'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="Activity Log ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      request_body=ActivityLogSerializer,
      responses={
          200: ActivityLogSerializer,
          400: 'Bad Request',
          404: 'Not Found'
      }
  )
  def put(self, request: Request, id):
    activity_log = self.get_activity_log(id)
    serializer = ActivityLogSerializer(activity_log, data = request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(data=serializer.data, status=status.HTTP_200_OK)
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @swagger_auto_schema(
      operation_summary="Delete activity log",
      operation_description="Delete an activity log",
      tags=['Activity Logs'],
      manual_parameters=[
          openapi.Parameter(
              'id',
              openapi.IN_PATH,
              description="Activity Log ID",
              type=openapi.TYPE_STRING,
              format=openapi.FORMAT_UUID
          )
      ],
      responses={
          204: 'No Content',
          404: 'Not Found'
      }
  )
  def delete(self, request: Request, id):
    activity_log = self.get_activity_log(id)
    activity_log.delete()
    return Response({'message': 'Activity log deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
