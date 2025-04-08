from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from financials.models.payable import Payable
from financials.serializers.payable import PayableSerializer


class PayableListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all payables",
        responses={200: PayableSerializer(many=True)}
    )
    def get(self, request: Request):
        payables = Payable.objects.all()
        serializer = PayableSerializer(payables, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new payable",
        request_body=PayableSerializer,
        responses={
            201: PayableSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = PayableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayableDetailView(APIView):
    def get_payable(self, id):
        try:
            payable = Payable.objects.get(pk=id)
            return payable
        except Payable.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific payable by ID",
        responses={
            200: PayableSerializer,
            404: "Payable not found"
        }
    )
    def get(self, request: Request, id):
        payable = self.get_payable(id)
        serializer = PayableSerializer(payable)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a payable",
        request_body=PayableSerializer,
        responses={
            200: PayableSerializer,
            400: "Invalid data",
            404: "Payable not found"
        }
    )
    def put(self, request: Request, id):
        payable = self.get_payable(id)
        serializer = PayableSerializer(payable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a payable",
        responses={
            204: "Payable deleted successfully",
            404: "Payable not found"
        }
    )
    def delete(self, request: Request, id):
        payable = self.get_payable(id)
        payable.delete()
        return Response({'message': 'Payable deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 