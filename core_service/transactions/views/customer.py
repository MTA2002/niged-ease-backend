# type: ignore
from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from drf_spectacular.utils import extend_schema, OpenApiResponse
from transactions.models.customer import Customer
from transactions.serializers.customer import CustomerSerializer


class CustomerListView(APIView):
    @extend_schema(
        description="Get a list of all customers for a specific store",
        responses={200: CustomerSerializer(many=True)}
    )
    def get(self, request: Request, store_id):
        customers = Customer.objects.filter(store_id=store_id)
        serializer = CustomerSerializer(customers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Create a new customer for a specific store",
        request=CustomerSerializer,
        responses={
            201: CustomerSerializer,
            400: OpenApiResponse(description="Invalid data")
        }
    )
    def post(self, request: Request, store_id):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    def get_customer(self, id, store_id):
        try:
            customer = Customer.objects.get(pk=id, store_id=store_id)
            return customer
        except Customer.DoesNotExist:
            raise Http404
    
    @extend_schema(
        description="Get a specific customer by ID for a specific store",
        responses={
            200: CustomerSerializer,
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def get(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        serializer = CustomerSerializer(customer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description="Update a customer for a specific store",
        request=CustomerSerializer,
        responses={
            200: CustomerSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def put(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        request.data['store_id'] = store_id
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Delete a customer for a specific store",
        responses={
            204: OpenApiResponse(description="Customer deleted successfully"),
            404: OpenApiResponse(description="Customer not found")
        }
    )
    def delete(self, request: Request, id, store_id):
        customer = self.get_customer(id, store_id)
        customer.delete()
        return Response({'message': 'Customer deleted successfully'}, status=status.HTTP_204_NO_CONTENT)