from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models.payment_mode import PaymentMode
from transactions.serializers.payment_mode import PaymentModeSerializer


class PaymentModeListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all payment modes",
        responses={200: PaymentModeSerializer(many=True)}
    )
    def get(self, request: Request):
        payment_modes = PaymentMode.objects.all()
        serializer = PaymentModeSerializer(payment_modes, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new payment mode",
        request_body=PaymentModeSerializer,
        responses={
            201: PaymentModeSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = PaymentModeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentModeDetailView(APIView):
    def get_payment_mode(self, id):
        try:
            payment_mode = PaymentMode.objects.get(pk=id)
            return payment_mode
        except PaymentMode.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific payment mode by ID",
        responses={
            200: PaymentModeSerializer,
            404: "Payment mode not found"
        }
    )
    def get(self, request: Request, id):
        payment_mode = self.get_payment_mode(id)
        serializer = PaymentModeSerializer(payment_mode)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a payment mode",
        request_body=PaymentModeSerializer,
        responses={
            200: PaymentModeSerializer,
            400: "Invalid data",
            404: "Payment mode not found"
        }
    )
    def put(self, request: Request, id):
        payment_mode = self.get_payment_mode(id)
        serializer = PaymentModeSerializer(payment_mode, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a payment mode",
        responses={
            204: "Payment mode deleted successfully",
            404: "Payment mode not found"
        }
    )
    def delete(self, request: Request, id):
        payment_mode = self.get_payment_mode(id)
        payment_mode.delete()
        return Response({'message': 'Payment mode deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 