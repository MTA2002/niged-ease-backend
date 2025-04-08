from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from transactions.models.customer import Customer
from transactions.serializers.customer import CustomerSerializer


class CustomerListView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of all customers",
        responses={200: CustomerSerializer(many=True)}
    )
    def get(self, request: Request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Create a new customer",
        request_body=CustomerSerializer,
        responses={
            201: CustomerSerializer,
            400: "Invalid data"
        }
    )
    def post(self, request: Request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    def get_customer(self, id):
        try:
            customer = Customer.objects.get(pk=id)
            return customer
        except Customer.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(
        operation_description="Get a specific customer by ID",
        responses={
            200: CustomerSerializer,
            404: "Customer not found"
        }
    )
    def get(self, request: Request, id):
        customer = self.get_customer(id)
        serializer = CustomerSerializer(customer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a customer",
        request_body=CustomerSerializer,
        responses={
            200: CustomerSerializer,
            400: "Invalid data",
            404: "Customer not found"
        }
    )
    def put(self, request: Request, id):
        customer = self.get_customer(id)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a customer",
        responses={
            204: "Customer deleted successfully",
            404: "Customer not found"
        }
    )
    def delete(self, request: Request, id):
        customer = self.get_customer(id)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT) 