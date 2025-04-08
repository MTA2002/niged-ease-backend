from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from financials.models.payment_in import PaymentIn
from financials.serializers.payment_in import PaymentInSerializer


class PaymentInListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all incoming payments",
        responses={200: PaymentInSerializer(many=True)}
    )
    def get(self, request: Request):
        payments = PaymentIn.objects.all()
        serializer = PaymentInSerializer(payments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new incoming payment",
        request_body=PaymentInSerializer,
        responses={
            201: PaymentInSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = PaymentInSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentInDetailView(APIView):
    def get_payment(self, id):
        try:
            payment = PaymentIn.objects.get(pk=id)
            return payment
        except PaymentIn.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific incoming payment by ID",
        responses={
            200: PaymentInSerializer,
            404: "Payment not found"
        }
    )
    def get(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentInSerializer(payment)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an incoming payment",
        request_body=PaymentInSerializer,
        responses={
            200: PaymentInSerializer,
            400: "Invalid data",
            404: "Payment not found"
        }
    )
    def put(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentInSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an incoming payment",
        responses={
            204: "Payment deleted successfully",
            404: "Payment not found"
        }
    )
    def delete(self, request: Request, id):
        payment = self.get_payment(id)
        payment.delete()
        return Response({'message': 'Payment in deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 