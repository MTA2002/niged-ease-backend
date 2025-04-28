from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from financials.models.payment_in import PaymentIn
from financials.serializers.payment_in import PaymentInSerializer


class PaymentInListView(APIView):
    @extend_schema(
        description="Get a list of all incoming payments",
        responses={200: PaymentInSerializer(many=True)}
    )
    def get(self, request: Request):
        payments = PaymentIn.objects.all()
        serializer = PaymentInSerializer(payments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new incoming payment",
        request=PaymentInSerializer,
        responses={
            201: PaymentInSerializer,
            400: OpenApiResponse(description="Invalid data")
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
    
    @extend_schema(
        description="Get a specific incoming payment by ID",
        responses={
            200: PaymentInSerializer,
            404: OpenApiResponse(description="Payment not found")
        }
    )
    def get(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentInSerializer(payment)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update an incoming payment",
        request=PaymentInSerializer,
        responses={
            200: PaymentInSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Payment not found")
        }
    )
    def put(self, request: Request, id):
        payment = self.get_payment(id)
        serializer = PaymentInSerializer(payment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete an incoming payment",
        responses={
            204: OpenApiResponse(description="Payment in deleted successfully"),
            404: OpenApiResponse(description="Payment not found")
        }
    )
    def delete(self, request: Request, id):
        payment = self.get_payment(id)
        payment.delete()
        return Response({'message': 'Payment in deleted successfully'}, status=status.HTTP_204_NO_CONTENT)