from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from financials.models.payment_out import PaymentOut
from financials.serializers.payment_out import PaymentOutSerializer


class PaymentOutListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all outgoing payments",
        responses={200: PaymentOutSerializer(many=True)}
    )
    def get(self, request: Request):
        payments = PaymentOut.objects.all()
        serializer = PaymentOutSerializer(payments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new outgoing payment",
        request_body=PaymentOutSerializer,
        responses={
            201: PaymentOutSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = PaymentOutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentOutDetailView(APIView):
    def get_payment(self, id):
        try:
            payment = PaymentOut.objects.get(pk=id)
            return payment
        except PaymentOut.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific outgoing payment by ID",
        responses={
            200: PaymentOutSerializer,
            404: "Payment not found"
        }
    )
    def get(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentOutSerializer(payment)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an outgoing payment",
        request_body=PaymentOutSerializer,
        responses={
            200: PaymentOutSerializer,
            400: "Invalid data",
            404: "Payment not found"
        }
    )
    def put(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentOutSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an outgoing payment",
        responses={
            204: "Payment deleted successfully",
            404: "Payment not found"
        }
    )
    def delete(self, request: Request, id):
        payment = self.get_payment(id)
        payment.delete()
        return Response({'message': 'Payment out deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 